"""
review2.py

Review 2 -- the changes requested by the guide at Review 1:

  A. Class balancing      (this module)
  B. Improve the result   (this module)
  C. Feature importance   (feature_importance.py)

PROTOCOL: identical to the reproduction in ensemble.run_repeated_cv --
stratified 10-fold CV x N_REPEATS with fold seeds 0..N_REPEATS-1, and every
scaler / resampler inside the pipeline so it is fit on the training fold only.
Every Review-2 number is therefore directly comparable with Review 1, and the
"partial" balancing configuration below reproduces the Review-1 ensemble
exactly (checked at run time).

OUTPUT: results/review2/{tables,figures}/ -- never results/tables/, so the
Review-1 reproduction numbers stay byte-identical and remain the baseline.

PRIMARY METRIC: macro-F1, fixed in config.REVIEW2_PRIMARY_METRIC before any of
these experiments was run. Accuracy is reported alongside it throughout.

Experiment A -- class balancing
-------------------------------
The same four learners and the paper's weighted soft vote, under four
balancing schemes, so the balancing is the only thing that changes:

  none          no balancing anywhere
  partial       Review 1: balanced class weights on SVM and RF only
  class_weight  balanced weights on all four (MLP and GradBoost have no
                class_weight parameter, so they get the equivalent per-sample
                weights through BalancedSampleWeight)
  smote         SMOTE oversampling of the training fold, no class weights

Experiment B -- improving the result
------------------------------------
  B1  Weight sharpening. Review 1 diagnosed that Eqs. (5) and (9) produce
      near-uniform weights, so the ensemble averages instead of exceeding its
      best member, and predicted that sharper weights should close the gap to
      Random Forest. A temperature T on the two normalisations tests that
      directly. This is a DIAGNOSTIC: the weights are computed from the same
      out-of-fold predictions they are scored on, so a T picked from this
      sweep is never reported as the improved result.
  B2  Stacking: replace the hand-built weights with a learned combiner (a
      logistic regression trained on the members' out-of-fold probabilities
      by sklearn's StackingClassifier, which runs its own inner 5-fold CV, so
      the combiner never sees the outer test fold). Same four members.
  B3  Stronger members: ExtraTrees and HistGradientBoosting, alone and
      stacked with Random Forest and SVM.
  B4  Learned temperature -- the fix the Review-1 diagnosis points to. The
      paper's ensemble, but the temperature (and whether it sharpens one term
      or both) is CHOSEN INSIDE EACH TRAINING FOLD by an inner 5-fold CV on
      the primary metric. The choice never sees the outer test fold, so --
      unlike the B1 sweep -- this is a legitimate result.
  B5  Stacking with a class-balanced combiner.

  B4 and B5 were added after a 1-repeat smoke test, which showed (i) that
  sharpening the weights helps, exactly as Review 1 predicted, and (ii) that
  the plain stacking combiner learns the majority-class bias back and discards
  the balancing. Both are principled fixes rather than tuning: B4's
  temperature is selected by nested CV, never from the B1 sweep, and B5 only
  makes the combiner consistent with its class-weighted members. The reported
  numbers come from the full 10-repeat run, not the smoke test.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from imblearn.over_sampling import SMOTE  # noqa: E402
from imblearn.pipeline import Pipeline as ImbPipeline  # noqa: E402
from sklearn.base import BaseEstimator, ClassifierMixin, clone  # noqa: E402
from sklearn.ensemble import (  # noqa: E402
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    StackingClassifier,
)
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import MinMaxScaler  # noqa: E402
from sklearn.utils.class_weight import compute_sample_weight  # noqa: E402

from base_learners import get_base_learners  # noqa: E402
from config import (  # noqa: E402
    N_SPLITS,
    RANDOM_STATE,
    REVIEW2_PRIMARY_METRIC,
    SMOTE_K_NEIGHBORS,
    WEIGHT_TEMPERATURES,
)
from ensemble import _error_vector, weighted_soft_vote  # noqa: E402

# Colours shared with the slide deck, so figures and slides read as one piece.
BERRY, ROSE, GOLD, INK, MUTED, SAGE = "#6D2E46", "#A26769", "#C8A45C", "#2B2B2B", "#9A9A9A", "#5B7F6B"

BALANCING_METHODS = ["none", "partial", "class_weight", "smote"]
BALANCING_LABELS = {
    "none": "No balancing",
    "partial": "Review 1 (SVM + RF only)",
    "class_weight": "Class weights, all four",
    "smote": "SMOTE oversampling",
}
PAPER_ENSEMBLE = "Ensemble (paper weights)"
MIXED_PAPER_ENSEMBLE = "Paper weights: SVM + RF + ExtraTrees + HistGB"
STACK_PAPER4 = "Stacked: paper's 4 learners (class-weighted)"
STACK_STRONG = "Stacked: SVM + RF + ExtraTrees + HistGB"
STACK_BALANCED = "Stacked: paper's 4 learners, balanced combiner"
LEARNED_T = "Learned-temperature ensemble"
LEARNED_T_CONFIGS = ["partial", "smote"]


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------
class BalancedSampleWeight(ClassifierMixin, BaseEstimator):
    """Fit `estimator` with 'balanced' per-sample weights computed from the
    labels it is given -- i.e. from the training fold only.

    GradientBoostingClassifier and MLPClassifier have no class_weight
    parameter, but both accept sample_weight in fit(). Giving each sample the
    weight n_samples / (n_classes * count(its class)) is exactly what
    class_weight='balanced' does inside SVM and Random Forest.
    """

    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, X, y):
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y, sample_weight=compute_sample_weight("balanced", y))
        self.classes_ = self.estimator_.classes_
        return self

    def predict(self, X):
        return self.estimator_.predict(X)

    def predict_proba(self, X):
        return self.estimator_.predict_proba(X)


def _pipe(estimator):
    return Pipeline([("scaler", MinMaxScaler()), ("clf", estimator)])


def make_paper_learners(balancing, random_state=RANDOM_STATE):
    """The reproduction's four learners under one balancing scheme.

    Everything is derived from base_learners.get_base_learners(), so the
    hyperparameters are identical to Review 1 and only the balancing changes.
    """
    learners = get_base_learners(random_state)
    if balancing == "partial":
        return learners

    if balancing in ("none", "smote"):
        learners["SVM"].set_params(clf__estimator__class_weight=None)
        learners["RF"].set_params(clf__class_weight=None)
    if balancing == "none":
        return learners

    if balancing == "class_weight":
        for name in ("MLP", "GradBoost"):
            learners[name].set_params(clf=BalancedSampleWeight(learners[name].named_steps["clf"]))
        return learners

    if balancing == "smote":
        # Oversample AFTER scaling (SMOTE interpolates between neighbours, so
        # it needs comparable feature scales) and only inside fit(), so the
        # test fold is never resampled.
        return {
            name: ImbPipeline(
                [
                    ("scaler", MinMaxScaler()),
                    ("smote", SMOTE(k_neighbors=SMOTE_K_NEIGHBORS, random_state=random_state)),
                    ("clf", pipe.named_steps["clf"]),
                ]
            )
            for name, pipe in learners.items()
        }

    raise ValueError(f"unknown balancing method: {balancing!r}")


def make_strong_learners(random_state=RANDOM_STATE):
    """Two members not in the paper, both class-weighted."""
    return {
        "ExtraTrees": _pipe(
            ExtraTreesClassifier(
                n_estimators=500, class_weight="balanced_subsample", random_state=random_state
            )
        ),
        "HistGB": _pipe(HistGradientBoostingClassifier(class_weight="balanced", random_state=random_state)),
    }


def make_stack(members, balanced_combiner=False, random_state=RANDOM_STATE):
    """A learned combiner in place of the paper's hand-built weights."""
    return StackingClassifier(
        estimators=list(members.items()),
        final_estimator=LogisticRegression(
            max_iter=5000, class_weight="balanced" if balanced_combiner else None
        ),
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state),
        stack_method="predict_proba",
        n_jobs=1,
    )


def strong_member_set(random_state=RANDOM_STATE):
    """SVM and RF (class-weighted) plus the two stronger learners."""
    cw = make_paper_learners("class_weight", random_state)
    return {"SVM": cw["SVM"], "RF": cw["RF"], **make_strong_learners(random_state)}


def _metric(y_true, y_pred, name):
    if name == "macro_f1":
        return f1_score(y_true, y_pred, average="macro", zero_division=0)
    if name == "accuracy":
        return accuracy_score(y_true, y_pred)
    raise ValueError(name)


class PaperWeightedEnsemble(ClassifierMixin, BaseEstimator):
    """Ma et al.'s weighted soft vote as an ordinary fit / predict estimator.

    In the cross-validation experiments the paper's weights are computed from
    each repeat's out-of-fold predictions, exactly as in Review 1. A standalone
    estimator cannot do that, so here the weights come from an inner
    cross-validation on the training data it is fitted on -- the same
    procedure, applied one level down.

    With the default temperatures=(1,) this is exactly the paper's scheme.
    Given several temperatures it becomes the Review-2 fix (B4): every
    (temperature, sharpen) pair is scored on the inner out-of-fold predictions
    and the best on `selection_metric` is kept. Ties go to the smaller
    temperature -- i.e. towards the paper's own setting.
    """

    def __init__(self, members, temperatures=(1,), sharpen_modes=("both",),
                 selection_metric=REVIEW2_PRIMARY_METRIC, inner_splits=5, random_state=RANDOM_STATE):
        self.members = members
        self.temperatures = temperatures
        self.sharpen_modes = sharpen_modes
        self.selection_metric = selection_metric
        self.inner_splits = inner_splits
        self.random_state = random_state

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        skf = StratifiedKFold(n_splits=self.inner_splits, shuffle=True, random_state=self.random_state)
        probas = {
            name: cross_val_predict(clone(model), X, y, cv=skf, method="predict_proba")
            for name, model in self.members.items()
        }
        errors = {n: _error_vector(y, self.classes_[p.argmax(axis=1)]) for n, p in probas.items()}

        best = None
        for T in sorted(self.temperatures):
            for mode in self.sharpen_modes:
                w = tempered_weights(errors, T, mode)
                pred = weighted_soft_vote(probas, w, list(self.classes_))
                value = _metric(y, pred, self.selection_metric)
                if best is None or value > best[0] + 1e-12:
                    best = (value, T, mode, w)
        self.inner_score_, self.temperature_, self.sharpen_, self.weights_ = best
        self.fitted_ = {name: clone(model).fit(X, y) for name, model in self.members.items()}
        return self

    def predict_proba(self, X):
        return sum(self.weights_[n] * m.predict_proba(X) for n, m in self.fitted_.items())

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


def make_learned_temperature(balancing, random_state=RANDOM_STATE):
    """B4: the paper's ensemble with the temperature chosen by inner CV."""
    return PaperWeightedEnsemble(
        make_paper_learners(balancing, random_state),
        temperatures=tuple(WEIGHT_TEMPERATURES),
        sharpen_modes=("both", "accuracy"),
        random_state=random_state,
    )


def estimator_for(model_name):
    """Map a row of model_comparison.csv back to an unfitted estimator."""
    if " | " in model_name:
        member, label = model_name.split(" | ")
        balancing = {v: k for k, v in BALANCING_LABELS.items()}[label]
        if member == LEARNED_T:
            return make_learned_temperature(balancing)
        learners = make_paper_learners(balancing)
        return PaperWeightedEnsemble(learners) if member == PAPER_ENSEMBLE else learners[member]
    if model_name in make_strong_learners():
        return make_strong_learners()[model_name]
    if model_name == MIXED_PAPER_ENSEMBLE:
        return PaperWeightedEnsemble(strong_member_set())
    if model_name == STACK_PAPER4:
        return make_stack(make_paper_learners("class_weight"))
    if model_name == STACK_STRONG:
        return make_stack(strong_member_set())
    if model_name == STACK_BALANCED:
        return make_stack(make_paper_learners("class_weight"), balanced_combiner=True)
    raise KeyError(f"no estimator registered for {model_name!r}")


def collect_oof_probas(X, y, learners, n_repeats, label="", n_splits=N_SPLITS, base_seed=0):
    """Out-of-fold predict_proba for every learner, per repeat, on exactly the
    folds ensemble.run_repeated_cv uses (same seeds), so results line up with
    Review 1 sample for sample."""
    per_repeat = []
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=base_seed + r)
        per_repeat.append(
            {
                name: cross_val_predict(model, X, y, cv=skf, n_jobs=-1, method="predict_proba")
                for name, model in learners.items()
            }
        )
        print(f"    [{label}] repeat {r + 1}/{n_repeats}", flush=True)
    return per_repeat


def labels_from(per_repeat, name, classes):
    return np.concatenate([np.asarray(classes)[p[name].argmax(axis=1)] for p in per_repeat])


def tempered_weights(error_vectors, temperature=1, sharpen="both"):
    """Eqs. (4)-(9) of Ma et al. with a temperature T on the normalisations:

        w_acc_i ∝ (1 / eps_i)^T      -- Eq. (5) at T = 1
        w_div_i ∝ D_i^T              -- Eq. (9) at T = 1
        w_i      = (w_acc_i + w_div_i) / 2   -- Eq. (4)

    T = 1 reproduces the paper exactly (x ** 1 is exact in floating point).
    `sharpen="accuracy"` applies T to the accuracy term only, which separates
    the effect of the two halves of the scheme.
    """
    names = list(error_vectors)
    t_acc = temperature
    t_div = temperature if sharpen == "both" else 1

    cv_err = {n: float(error_vectors[n].mean()) for n in names}
    inv = {n: (1.0 / cv_err[n] if cv_err[n] > 0 else 1e6) ** t_acc for n in names}
    total_inv = sum(inv.values())
    w_acc = {n: inv[n] / total_inv for n in names}

    D = {
        n: sum(np.linalg.norm(error_vectors[n] - error_vectors[o]) for o in names if o != n)
        for n in names
    }
    Dt = {n: D[n] ** t_div for n in names}
    total_D = sum(Dt.values())
    w_div = {n: Dt[n] / total_D for n in names}

    w = {n: 0.5 * (w_acc[n] + w_div[n]) for n in names}
    if not all(np.isfinite(v) for v in w.values()):
        raise FloatingPointError(f"non-finite weights at T={temperature}")
    return w


def paper_weighted_ensemble(per_repeat, y, classes, temperature=1, sharpen="both"):
    """The paper's weighted soft vote, recomputed per repeat as in Review 1."""
    preds, weights = [], []
    for probas in per_repeat:
        fold_preds = {n: np.asarray(classes)[p.argmax(axis=1)] for n, p in probas.items()}
        errs = {n: _error_vector(y, fold_preds[n]) for n in probas}
        w = tempered_weights(errs, temperature, sharpen)
        preds.append(weighted_soft_vote(probas, w, classes))
        weights.append(w)
    return np.concatenate(preds), weights


def score(y_true, y_pred, classes):
    """Accuracy, balanced accuracy, macro / weighted F1 and per-class recall (%).

    Per-class recall is the metric Ma et al. call "precision" -- see the
    terminology note in evaluate.py.
    """
    recall = recall_score(y_true, y_pred, labels=classes, average=None, zero_division=0)
    row = {
        "accuracy": 100 * accuracy_score(y_true, y_pred),
        "balanced_accuracy": 100 * balanced_accuracy_score(y_true, y_pred),
        "macro_f1": 100 * f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0),
        "weighted_f1": 100 * f1_score(y_true, y_pred, labels=classes, average="weighted", zero_division=0),
    }
    for c, r in zip(classes, recall):
        row[f"recall_{c}"] = 100 * r
    return row


# --------------------------------------------------------------------------
# Experiment A -- class balancing
# --------------------------------------------------------------------------
def experiment_a_class_balancing(X, y, classes, n_repeats, tables_dir, figures_dir):
    y_pooled = np.concatenate([y] * n_repeats)
    rows, cache = [], {}

    preds = {}
    for b in BALANCING_METHODS:
        print(f"  A. balancing = {b}", flush=True)
        learners = make_paper_learners(b)
        per_repeat = collect_oof_probas(X, y, learners, n_repeats, label=b)
        cache[b] = per_repeat
        for name in learners:
            pred = labels_from(per_repeat, name, classes)
            preds[f"{name} | {BALANCING_LABELS[b]}"] = pred
            rows.append({"balancing": b, "model": name, **score(y_pooled, pred, classes)})
        ens, _ = paper_weighted_ensemble(per_repeat, y, classes)
        preds[f"{PAPER_ENSEMBLE} | {BALANCING_LABELS[b]}"] = ens
        rows.append({"balancing": b, "model": PAPER_ENSEMBLE, **score(y_pooled, ens, classes)})

    df = pd.DataFrame(rows)
    df.insert(1, "balancing_label", df["balancing"].map(BALANCING_LABELS))
    df.round(4).to_csv(tables_dir / "A_class_balancing.csv", index=False)

    ens_rows = df[df["model"] == PAPER_ENSEMBLE].set_index("balancing").loc[BALANCING_METHODS]
    _plot_balancing(ens_rows, classes, figures_dir)
    return df, cache, preds


def _plot_balancing(ens_rows, classes, figures_dir):
    labels = [BALANCING_LABELS[b] for b in ens_rows.index]
    colours = [MUTED, ROSE, BERRY, GOLD]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    x = np.arange(len(labels))
    ax.bar(x - 0.2, ens_rows["accuracy"], 0.4, label="Accuracy", color=MUTED)
    ax.bar(x + 0.2, ens_rows["macro_f1"], 0.4, label="Macro-F1 (primary)", color=BERRY)
    for i, (a, f) in enumerate(zip(ens_rows["accuracy"], ens_rows["macro_f1"])):
        ax.text(i - 0.2, a + 0.8, f"{a:.1f}", ha="center", fontsize=9)
        ax.text(i + 0.2, f + 0.8, f"{f:.1f}", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=12, ha="right")
    ax.set_ylabel("%")
    ax.set_ylim(0, 85)
    ax.set_title("Paper-weighted ensemble under each balancing scheme")
    ax.legend(frameon=False)

    ax = axes[1]
    cx = np.arange(len(classes))
    width = 0.2
    for i, (b, colour) in enumerate(zip(ens_rows.index, colours)):
        vals = [ens_rows.loc[b, f"recall_{c}"] for c in classes]
        ax.bar(cx + (i - 1.5) * width, vals, width, label=BALANCING_LABELS[b], color=colour)
    ax.set_xticks(cx)
    ax.set_xticklabels([str(c) for c in classes])
    ax.set_xlabel("Quality class")
    ax.set_ylabel("Recall (%)  [the paper's 'precision']")
    ax.set_ylim(0, 100)
    ax.set_title("Per-class recall: where balancing helps")
    ax.legend(frameon=False, fontsize=8)

    for a in axes:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures_dir / "A_class_balancing.png", dpi=170)
    plt.close(fig)


# --------------------------------------------------------------------------
# Experiment B -- improving the result
# --------------------------------------------------------------------------
def experiment_b1_temperature(cache, y, classes, configs, tables_dir, figures_dir):
    """Diagnostic sweep -- see module docstring for why it is never used to
    pick the final model."""
    n_repeats = len(next(iter(cache.values())))
    y_pooled = np.concatenate([y] * n_repeats)
    rows = []
    for cfg in configs:
        rf_acc = score(y_pooled, labels_from(cache[cfg], "RF", classes), classes)["accuracy"]
        for sharpen in ("both", "accuracy"):
            for T in WEIGHT_TEMPERATURES:
                ens, ws = paper_weighted_ensemble(cache[cfg], y, classes, temperature=T, sharpen=sharpen)
                mean_w = {n: float(np.mean([w[n] for w in ws])) for n in ws[0]}
                top = max(mean_w, key=mean_w.get)
                rows.append(
                    {
                        "balancing": cfg,
                        "sharpen": sharpen,
                        "temperature": T,
                        **score(y_pooled, ens, classes),
                        "rf_accuracy": rf_acc,
                        "largest_weight_learner": top,
                        "largest_weight": mean_w[top],
                        **{f"w_{n}": v for n, v in mean_w.items()},
                    }
                )
    df = pd.DataFrame(rows)
    df.round(4).to_csv(tables_dir / "B1_weight_temperature.csv", index=False)
    _plot_temperature(df, figures_dir)
    return df


def _plot_temperature(df, figures_dir):
    cfgs = list(dict.fromkeys(df["balancing"]))
    fig, axes = plt.subplots(1, len(cfgs), figsize=(6.5 * len(cfgs), 4.6), squeeze=False)
    for ax, cfg in zip(axes[0], cfgs):
        sub = df[df["balancing"] == cfg]
        for sharpen, colour, label in (
            ("accuracy", BERRY, "Sharpen accuracy term only"),
            ("both", GOLD, "Sharpen both terms"),
        ):
            s = sub[sub["sharpen"] == sharpen]
            ax.plot(s["temperature"], s["accuracy"], marker="o", color=colour, label=label)
        ax.axhline(sub["rf_accuracy"].iloc[0], color=INK, ls="--", lw=1, label="Random Forest alone")
        ax.set_xscale("log")
        ax.set_xticks(sorted(sub["temperature"].unique()))
        ax.set_xticklabels([str(t) for t in sorted(sub["temperature"].unique())])
        ax.set_xlabel("Temperature T  (T = 1 is the paper)")
        ax.set_ylabel("Ensemble accuracy (%)")
        ax.set_title(f"Weight sharpening -- {BALANCING_LABELS[cfg]}")
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "B1_weight_temperature.png", dpi=170)
    plt.close(fig)


def experiment_b2_b3_improvements(X, y, classes, n_repeats, cache, tables_dir):
    """Stacking (same four members) and stronger members."""
    y_pooled = np.concatenate([y] * n_repeats)
    rows = []
    cw = make_paper_learners("class_weight")
    strong = make_strong_learners()

    preds = {}
    print("  B3. stronger single learners", flush=True)
    strong_probas = collect_oof_probas(X, y, strong, n_repeats, label="strong singles")
    for name in strong:
        preds[name] = labels_from(strong_probas, name, classes)
        rows.append({"model": name, "kind": "single learner", **score(y_pooled, preds[name], classes)})

    # The paper's weighting scheme, applied to the stronger member set
    # (probabilities reused -- no refitting).
    mixed = [
        {"SVM": c["SVM"], "RF": c["RF"], "ExtraTrees": s["ExtraTrees"], "HistGB": s["HistGB"]}
        for c, s in zip(cache["class_weight"], strong_probas)
    ]
    ens, _ = paper_weighted_ensemble(mixed, y, classes)
    preds[MIXED_PAPER_ENSEMBLE] = ens
    rows.append({"model": MIXED_PAPER_ENSEMBLE, "kind": "ensemble", **score(y_pooled, ens, classes)})

    stacks = {
        STACK_PAPER4: make_stack(cw),
        STACK_BALANCED: make_stack(cw, balanced_combiner=True),
        STACK_STRONG: make_stack(strong_member_set()),
    }
    for name, stack in stacks.items():
        print(f"  B2. {name}", flush=True)
        probas = collect_oof_probas(X, y, {name: stack}, n_repeats, label="stack")
        preds[name] = labels_from(probas, name, classes)
        rows.append({"model": name, "kind": "ensemble", **score(y_pooled, preds[name], classes)})

    print("  B4. learned-temperature ensemble (temperature chosen by inner CV)", flush=True)
    chosen_rows = []
    for balancing in LEARNED_T_CONFIGS:
        name = f"{LEARNED_T} | {BALANCING_LABELS[balancing]}"
        pred, chosen = _oof_learned_temperature(X, y, balancing, n_repeats)
        preds[name] = pred
        rows.append({"model": name, "kind": "ensemble", **score(y_pooled, pred, classes)})
        chosen_rows += [{"balancing": balancing, **c} for c in chosen]

    chosen_df = pd.DataFrame(chosen_rows)
    chosen_df.to_csv(tables_dir / "B4_chosen_temperatures.csv", index=False)
    plot_chosen_temperatures(chosen_df, tables_dir.parent / "figures")

    df = pd.DataFrame(rows)
    df.round(4).to_csv(tables_dir / "B2_B3_improvements.csv", index=False)
    return df, preds


def plot_chosen_temperatures(chosen_df, figures_dir):
    """How often each outer fold's inner CV picked each temperature."""
    temps = sorted(chosen_df["temperature"].unique())
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    x = np.arange(len(temps))
    for i, (b, colour, label) in enumerate((("partial", BERRY, "Review-1 members"), ("smote", GOLD, "SMOTE members"))):
        sub = chosen_df[chosen_df["balancing"] == b]
        if sub.empty:
            continue
        counts = [int((sub["temperature"] == t).sum()) for t in temps]
        bars = ax.bar(x + (i - 0.5) * 0.38, counts, 0.38, color=colour, label=label)
        ax.bar_label(bars, fontsize=8, padding=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"T = {t:g}" + ("\n(paper)" if t == 1 else "") for t in temps], fontsize=9)
    ax.set_ylabel("Number of folds")
    ax.set_title("Temperature chosen by each fold's inner CV", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(figures_dir / "B4_chosen_temperatures.png", dpi=170)
    plt.close(fig)


def _oof_learned_temperature(X, y, balancing, n_repeats, n_splits=N_SPLITS):
    """Pooled out-of-fold predictions for B4 on the Review-1 folds, plus the
    temperature each outer fold's inner CV chose."""
    preds, chosen = [], []
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=r)
        cv = cross_validate(make_learned_temperature(balancing), X, y, cv=skf,
                            return_estimator=True, return_indices=True, n_jobs=-1)
        oof = np.empty_like(y)
        for fold, (est, test) in enumerate(zip(cv["estimator"], cv["indices"]["test"])):
            oof[test] = est.predict(X[test])
            chosen.append({"repeat": r, "fold": fold, "temperature": est.temperature_,
                           "sharpen": est.sharpen_, "inner_score": est.inner_score_,
                           **{f"w_{n}": v for n, v in est.weights_.items()}})
        preds.append(oof)
        print(f"    [learned T, {balancing}] repeat {r + 1}/{n_repeats}", flush=True)
    return np.concatenate(preds), chosen


# --------------------------------------------------------------------------
# Putting A and B together
# --------------------------------------------------------------------------
def build_model_comparison(a_df, b_df, tables_dir):
    """Every candidate the project evaluated, ranked on the primary metric.

    Selection is made on the same cross-validation that scores the candidates,
    so the winner's score carries a small optimistic bias; with this few
    candidates it is small, and it is disclosed rather than hidden. The
    temperature sweep (B1) is excluded on purpose -- see the module docstring.
    """
    a_part = a_df.copy()
    a_part["model"] = a_part.apply(
        lambda r: f"{r['model']} | {BALANCING_LABELS[r['balancing']]}", axis=1
    )
    a_part["kind"] = np.where(
        a_part["model"].str.startswith(PAPER_ENSEMBLE), "ensemble", "single learner"
    )
    a_part["experiment"] = "A. class balancing"
    b_part = b_df.copy()
    b_part["experiment"] = "B. improvements"

    cols = ["experiment", "model", "kind"] + [c for c in a_df.columns if c not in ("balancing", "balancing_label", "model")]
    comp = pd.concat([a_part[cols], b_part[cols]], ignore_index=True)
    comp = comp.sort_values(REVIEW2_PRIMARY_METRIC, ascending=False).reset_index(drop=True)
    comp.insert(0, "rank_by_" + REVIEW2_PRIMARY_METRIC, comp.index + 1)
    comp.round(4).to_csv(tables_dir / "model_comparison.csv", index=False)
    return comp


def headline_table(a_df, comp, tables_dir):
    """Review 1 baseline vs the best Review-2 model, side by side."""
    base = a_df[(a_df["balancing"] == "partial") & (a_df["model"] == PAPER_ENSEMBLE)].iloc[0]
    rf = a_df[(a_df["balancing"] == "partial") & (a_df["model"] == "RF")].iloc[0]
    best = comp.iloc[0]
    metrics = [c for c in comp.columns if c in base.index and c not in ("model", "balancing", "balancing_label")]
    out = pd.DataFrame(
        {
            "metric": metrics,
            "review1_ensemble": [base[m] for m in metrics],
            "review1_random_forest": [rf[m] for m in metrics],
            "review2_best": [best[m] for m in metrics],
        }
    )
    out["change_vs_review1_ensemble"] = out["review2_best"] - out["review1_ensemble"]
    out.round(4).to_csv(tables_dir / "headline_review1_vs_review2.csv", index=False)
    with open(tables_dir / "headline_best_model.txt", "w") as f:
        f.write(str(best["model"]) + "\n")
    return out, best["model"]


def plot_headline(comp, figures_dir, top_n=8):
    ens = comp[comp["kind"] == "ensemble"].head(top_n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(ens) + 1.6))
    y_pos = np.arange(len(ens))
    ax.barh(y_pos - 0.2, ens["macro_f1"], 0.4, color=BERRY, label="Macro-F1 (primary)")
    ax.barh(y_pos + 0.2, ens["accuracy"], 0.4, color=MUTED, label="Accuracy")
    for i, (f, a) in enumerate(zip(ens["macro_f1"], ens["accuracy"])):
        ax.text(f + 0.4, i - 0.2, f"{f:.2f}", va="center", fontsize=8)
        ax.text(a + 0.4, i + 0.2, f"{a:.2f}", va="center", fontsize=8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([m.replace(" | ", "\n") for m in ens["model"]], fontsize=8)
    ax.set_xlabel("%")
    ax.set_xlim(0, 85)
    ax.set_title("Ensembles ranked by macro-F1")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(figures_dir / "B_model_comparison.png", dpi=170)
    plt.close(fig)


def plot_tradeoff(comp, figures_dir):
    """Every candidate as a point: accuracy (x) against macro-F1 (y).

    The upper-right boundary (the Pareto frontier) is the set of models no
    other model beats on BOTH metrics at once -- the honest answer to "which
    model is best" when the two metrics disagree.
    """
    d = comp.copy()
    pts = d[["accuracy", "macro_f1"]].to_numpy()
    on_front = np.array([
        not np.any((pts[:, 0] >= a) & (pts[:, 1] >= f) & ((pts[:, 0] > a) | (pts[:, 1] > f)))
        for a, f in pts
    ])
    d["pareto"] = on_front

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    singles = d[d["kind"] == "single learner"]
    ensembles = d[d["kind"] == "ensemble"]
    ax.scatter(singles["accuracy"], singles["macro_f1"], s=36, color=MUTED, alpha=0.75, label="Single learner")
    ax.scatter(ensembles["accuracy"], ensembles["macro_f1"], s=52, color=ROSE, alpha=0.9, label="Ensemble")

    front = d[d["pareto"]].sort_values("accuracy")
    ax.plot(front["accuracy"], front["macro_f1"], color=BERRY, lw=1.6, ls="--", label="Best trade-off frontier")
    ax.scatter(front["accuracy"], front["macro_f1"], s=80, facecolor="none", edgecolor=BERRY, lw=1.6)

    def mark(name, label, colour, dx, dy):
        row = d[d["model"] == name]
        if row.empty:
            return
        a, f = row["accuracy"].iloc[0], row["macro_f1"].iloc[0]
        ax.scatter([a], [f], s=95, color=colour, zorder=6, edgecolor=INK, lw=0.6)
        ax.annotate(label, (a, f), textcoords="offset points", xytext=(dx, dy), fontsize=8.5,
                    color=INK, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.7})

    mark(f"{PAPER_ENSEMBLE} | {BALANCING_LABELS['partial']}", "Review 1 ensemble", GOLD, -95, -22)
    mark(f"RF | {BALANCING_LABELS['partial']}", "Review 1 Random Forest", GOLD, 10, -26)
    best = d.sort_values(REVIEW2_PRIMARY_METRIC, ascending=False).iloc[0]
    mark(best["model"], "Best on macro-F1", BERRY, -120, 10)
    top_acc = d.sort_values("accuracy", ascending=False).iloc[0]
    mark(top_acc["model"], "Best on accuracy", SAGE, -10, 22)

    # Zoom to where the ensembles sit; say how many weaker points fall off the
    # left edge rather than dropping them silently.
    x_lo = float(np.floor(ensembles["accuracy"].min() - 2))
    y_lo = float(np.floor(d.loc[d["accuracy"] >= x_lo, "macro_f1"].min() - 1))
    hidden = int((d["accuracy"] < x_lo).sum())
    ax.set_xlim(x_lo, float(np.ceil(d["accuracy"].max() + 1)))
    ax.set_ylim(y_lo, float(np.ceil(d["macro_f1"].max() + 1)))
    if hidden:
        ax.text(0.01, 0.01, f"{hidden} weaker single learners (accuracy < {x_lo:.0f}%) lie off the left edge",
                transform=ax.transAxes, fontsize=8, color=MUTED, ha="left", va="bottom")

    ax.set_xlabel("Accuracy (%)  -- rewards getting the common classes right")
    ax.set_ylabel("Macro-F1 (%)  -- weights all six classes equally")
    ax.set_title("No model wins both: the accuracy vs. rare-class trade-off")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(figures_dir / "B_tradeoff.png", dpi=170)
    plt.close(fig)
    return d


def per_repeat_scores(all_preds, y, classes, n_repeats):
    """Split every candidate's pooled predictions back into its 10 repeats.

    Pooled predictions are the concatenation of the repeats in order (seed 0,
    1, ...), so slice r is exactly repeat r -- and every candidate was scored
    on the same folds in the same repeat, which makes the comparison paired.
    """
    n = len(y)
    rows = []
    for name, pred in all_preds.items():
        for r in range(n_repeats):
            s = score(y, pred[r * n:(r + 1) * n], classes)
            rows.append({"model": name, "repeat": r, "accuracy": s["accuracy"],
                         "balanced_accuracy": s["balanced_accuracy"], "macro_f1": s["macro_f1"]})
    return pd.DataFrame(rows)


def paired_comparison(per_rep, pairs, tables_dir):
    """Is a difference consistent across the repeats, or noise?

    For each (model, comparator) pair: the mean and spread of the per-repeat
    difference, how many repeats the model wins, and a Wilcoxon signed-rank
    test. CAVEAT: the repeats reuse the same 1,599 wines with different splits,
    so they are not independent samples and the p-value is optimistic. The
    win count is the plainer evidence; the p-value is indicative only.
    """
    from scipy.stats import wilcoxon

    rows = []
    for model, other in pairs:
        a = per_rep[per_rep["model"] == model].sort_values("repeat")
        b = per_rep[per_rep["model"] == other].sort_values("repeat")
        if a.empty or b.empty or model == other:
            continue
        for metric in ("macro_f1", "accuracy"):
            d = a[metric].to_numpy() - b[metric].to_numpy()
            p = float(wilcoxon(d).pvalue) if len(d) > 1 and np.any(d != 0) else np.nan
            rows.append({"model": model, "compared_with": other, "metric": metric,
                         "mean_difference": d.mean(), "sd_difference": d.std(ddof=1) if len(d) > 1 else np.nan,
                         "repeats_won": int((d > 0).sum()), "repeats_tied": int((d == 0).sum()),
                         "repeats": len(d), "wilcoxon_p": p})
    out = pd.DataFrame(rows)
    out.round(6).to_csv(tables_dir / "paired_comparison.csv", index=False)
    return out


def save_confusion(y_true, y_pred, classes, name, tables_dir):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    pd.DataFrame(cm, index=[f"true_{c}" for c in classes], columns=[f"pred_{c}" for c in classes]).to_csv(
        tables_dir / f"confusion_matrix_{name}.csv"
    )
    return cm
