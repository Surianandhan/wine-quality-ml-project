"""
feature_importance.py

Review 2, Experiment C -- which of the 11 lab measurements drive the model?

No single importance measure is trustworthy on its own, so three are used and
checked against each other:

  1. PERMUTATION IMPORTANCE (primary). Shuffle one feature inside the held-out
     test fold and measure how much macro-F1 falls. It is model-agnostic and is
     computed on data the model never trained on, so it measures what the
     model actually relies on. Averaged over the 10 test folds, with
     PERMUTATION_REPEATS shuffles per feature per fold.
  2. RANDOM FOREST IMPURITY IMPORTANCE (MDI). Comes free with the forest but is
     known to favour continuous, many-valued features -- shown for comparison,
     never as the headline.
  3. DIRECTION. Spearman rank correlation of each feature with quality on the
     full dataset. Importance says how much a feature matters; this says which
     way it pushes quality. It is descriptive and never feeds a prediction.

Then a practical test: retrain with only the top-k features, chosen INSIDE each
training fold. Choosing them on the full dataset first would leak test-fold
information into the choice. It answers "how many lab tests are needed?", plus
a direct check of the four attributes Ma et al. highlight (Figs. 4-5).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.feature_selection import SelectFromModel  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_validate  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import MinMaxScaler  # noqa: E402

from base_learners import get_base_learners  # noqa: E402
from config import (  # noqa: E402
    FEATURE_SUBSET_SIZES,
    N_SPLITS,
    PAPER_KEY_ATTRIBUTES,
    PERMUTATION_REPEATS,
    RANDOM_STATE,
)
from review2 import BERRY, GOLD, INK, MUTED, ROSE, SAGE, estimator_for, score  # noqa: E402


# --------------------------------------------------------------------------
# 1 + 2. Permutation importance (and MDI where the model has it)
# --------------------------------------------------------------------------
def _one_fold(model, X, y, train, test, fold, seed):
    fitted = clone(model).fit(X[train], y[train])
    result = permutation_importance(
        fitted,
        X[test],
        y[test],
        scoring=["f1_macro", "accuracy"],
        n_repeats=PERMUTATION_REPEATS,
        random_state=seed + fold,
        n_jobs=1,
    )
    mdi = None
    clf = getattr(fitted, "named_steps", {}).get("clf")
    if clf is not None and hasattr(clf, "feature_importances_"):
        mdi = clf.feature_importances_
    return result["f1_macro"].importances_mean, result["accuracy"].importances_mean, mdi


def permutation_importance_cv(model, X, y, feature_names, seed=0, n_splits=N_SPLITS):
    """Permutation importance on each held-out fold of one stratified 10-fold
    split, in percentage points of macro-F1 / accuracy lost."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = Parallel(n_jobs=-1)(
        delayed(_one_fold)(model, X, y, tr, te, k, seed) for k, (tr, te) in enumerate(skf.split(X, y))
    )
    f1 = 100 * np.array([f[0] for f in folds])
    acc = 100 * np.array([f[1] for f in folds])
    out = pd.DataFrame(
        {
            "feature": feature_names,
            "f1_drop_mean": f1.mean(axis=0),
            "f1_drop_std": f1.std(axis=0),
            "accuracy_drop_mean": acc.mean(axis=0),
            "accuracy_drop_std": acc.std(axis=0),
        }
    )
    if all(f[2] is not None for f in folds):
        out["mdi_mean"] = np.array([f[2] for f in folds]).mean(axis=0)
    return out


# --------------------------------------------------------------------------
# 3. Direction of effect
# --------------------------------------------------------------------------
def direction_of_effect(X, y, feature_names):
    rows = []
    for j, name in enumerate(feature_names):
        rho, p = spearmanr(X[:, j], y)
        rows.append({"feature": name, "spearman_rho": rho, "p_value": p})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Practical test: how many lab tests are needed?
# --------------------------------------------------------------------------
def _rf(n_estimators):
    return RandomForestClassifier(
        n_estimators=n_estimators, class_weight="balanced_subsample", random_state=RANDOM_STATE
    )


def _oof_with_selection(model, X, y, n_repeats, n_splits=N_SPLITS):
    """Pooled out-of-fold predictions on the Review-1 folds, plus which
    features the in-fold selector kept each time."""
    preds, kept = [], []
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=r)
        cv = cross_validate(model, X, y, cv=skf, return_estimator=True, return_indices=True, n_jobs=-1)
        oof = np.empty_like(y)
        for est, test in zip(cv["estimator"], cv["indices"]["test"]):
            oof[test] = est.predict(X[test])
            if "select" in est.named_steps:
                kept.append(est.named_steps["select"].get_support())
        preds.append(oof)
    return np.concatenate(preds), (np.array(kept) if kept else None)


def feature_subset_curve(X, y, classes, feature_names, n_repeats):
    y_pooled = np.concatenate([y] * n_repeats)
    rows, freq_rows = [], []

    for k in FEATURE_SUBSET_SIZES:
        print(f"    top-{k} features", flush=True)
        model = Pipeline(
            [
                ("scaler", MinMaxScaler()),
                ("select", SelectFromModel(_rf(200), max_features=k, threshold=-np.inf)),
                ("clf", _rf(300)),
            ]
        )
        pred, kept = _oof_with_selection(model, X, y, n_repeats)
        freq = kept.mean(axis=0)
        top = [feature_names[i] for i in np.argsort(-freq)[:k]]
        rows.append({"subset": f"top {k} (chosen in-fold)", "n_features": k, **score(y_pooled, pred, classes),
                     "features_most_often_chosen": "; ".join(top)})
        freq_rows.append({"n_features": k, **{f: 100 * v for f, v in zip(feature_names, freq)}})

    # The paper's four, taken at face value (no selection step).
    print("    paper's four key attributes", flush=True)
    idx = [feature_names.index(f) for f in PAPER_KEY_ATTRIBUTES]
    model = Pipeline([("scaler", MinMaxScaler()), ("clf", _rf(300))])
    pred, _ = _oof_with_selection(model, X[:, idx], y, n_repeats)
    rows.append({"subset": "Ma et al.'s 4 key attributes", "n_features": len(idx), **score(y_pooled, pred, classes),
                 "features_most_often_chosen": "; ".join(PAPER_KEY_ATTRIBUTES)})

    return pd.DataFrame(rows), pd.DataFrame(freq_rows)


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)


def plot_permutation(final_imp, rf_imp, final_name, figures_dir):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
    for ax, imp, title in ((axes[0], final_imp, f"Best Review-2 model\n{final_name}"),
                           (axes[1], rf_imp, "Random Forest (Review-1 configuration)")):
        d = imp.sort_values("f1_drop_mean")
        colours = [GOLD if f in PAPER_KEY_ATTRIBUTES else BERRY for f in d["feature"]]
        ax.barh(d["feature"], d["f1_drop_mean"], xerr=d["f1_drop_std"], color=colours,
                error_kw={"ecolor": MUTED, "elinewidth": 1})
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_xlabel("Macro-F1 lost when the feature is shuffled (percentage points)")
        ax.set_title(title, fontsize=10)
        _style(ax)
    # Explicit patches: legend entries from empty bar() calls lose their colour.
    axes[1].legend(handles=[Patch(color=GOLD, label="Highlighted by Ma et al. (Figs. 4-5)"),
                            Patch(color=BERRY, label="Other features")],
                   frameon=False, loc="lower right", fontsize=8)
    fig.suptitle("Permutation importance on held-out folds (error bars: spread across the 10 folds)", fontsize=11)
    fig.tight_layout()
    fig.savefig(figures_dir / "C1_permutation_importance.png", dpi=170)
    plt.close(fig)


def plot_methods_and_direction(table, figures_dir):
    d = table.sort_values("final_f1_drop", ascending=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)

    ax = axes[0]
    shares = {
        "Permutation, best model": d["final_f1_drop"].clip(lower=0) / d["final_f1_drop"].clip(lower=0).sum(),
        "Permutation, Random Forest": d["rf_f1_drop"].clip(lower=0) / d["rf_f1_drop"].clip(lower=0).sum(),
        "Impurity (MDI), Random Forest": d["rf_mdi"] / d["rf_mdi"].sum(),
    }
    y_pos = np.arange(len(d))
    for i, ((label, vals), colour) in enumerate(zip(shares.items(), (BERRY, ROSE, MUTED))):
        ax.barh(y_pos + (i - 1) * 0.27, 100 * vals, 0.27, color=colour, label=label)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(d["feature"])
    ax.set_xlabel("Share of total importance (%)")
    ax.set_title("Three importance measures, side by side", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    _style(ax)

    ax = axes[1]
    colours = [SAGE if r > 0 else BERRY for r in d["spearman_rho"]]
    ax.barh(y_pos, d["spearman_rho"], color=colours)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlim(-0.55, 0.55)
    ax.set_xlabel("Spearman correlation with quality")
    ax.set_title("Direction: higher value -> higher (green) or lower (red) quality", fontsize=10)
    _style(ax)

    fig.tight_layout()
    fig.savefig(figures_dir / "C2_importance_methods_and_direction.png", dpi=170)
    plt.close(fig)


def plot_subset_curve(curve, figures_dir):
    topk = curve[curve["subset"].str.startswith("top")]
    paper = curve[~curve["subset"].str.startswith("top")].iloc[0]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(topk["n_features"], topk["accuracy"], marker="o", color=MUTED, label="Accuracy")
    ax.plot(topk["n_features"], topk["macro_f1"], marker="o", color=BERRY, label="Macro-F1 (primary)")
    ax.scatter([paper["n_features"]], [paper["accuracy"]], marker="D", s=70, color=GOLD, zorder=5,
               label="Ma et al.'s 4 attributes (accuracy)")
    ax.scatter([paper["n_features"]], [paper["macro_f1"]], marker="D", s=70, color=GOLD, edgecolor=INK, zorder=5,
               label="Ma et al.'s 4 attributes (macro-F1)")
    for _, r in topk.iterrows():
        ax.annotate(f"{r['accuracy']:.1f}", (r["n_features"], r["accuracy"]), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=8)
        ax.annotate(f"{r['macro_f1']:.1f}", (r["n_features"], r["macro_f1"]), textcoords="offset points",
                    xytext=(0, -13), ha="center", fontsize=8)
    ax.set_xticks(FEATURE_SUBSET_SIZES)
    ax.set_xlabel("Number of lab measurements used (chosen inside each training fold)")
    ax.set_ylabel("%")
    ax.set_title("How many lab tests does the model need?  (Random Forest, class-weighted)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    _style(ax)
    fig.tight_layout()
    fig.savefig(figures_dir / "C3_feature_subset.png", dpi=170)
    plt.close(fig)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def run_feature_importance(X, y, classes, feature_names, final_model_name, n_repeats, tables_dir, figures_dir):
    feature_names = list(feature_names)

    print(f"  C1. permutation importance -- best model: {final_model_name}", flush=True)
    final_imp = permutation_importance_cv(estimator_for(final_model_name), X, y, feature_names)
    print("  C1. permutation importance -- Random Forest", flush=True)
    rf_imp = permutation_importance_cv(get_base_learners()["RF"], X, y, feature_names)
    direction = direction_of_effect(X, y, feature_names)

    table = pd.DataFrame({"feature": feature_names})
    table["final_f1_drop"] = final_imp["f1_drop_mean"].values
    table["final_f1_drop_std"] = final_imp["f1_drop_std"].values
    table["final_accuracy_drop"] = final_imp["accuracy_drop_mean"].values
    table["rf_f1_drop"] = rf_imp["f1_drop_mean"].values
    table["rf_f1_drop_std"] = rf_imp["f1_drop_std"].values
    table["rf_accuracy_drop"] = rf_imp["accuracy_drop_mean"].values
    table["rf_mdi"] = rf_imp["mdi_mean"].values
    table = table.merge(direction, on="feature")
    table["rank_final"] = table["final_f1_drop"].rank(ascending=False).astype(int)
    table["rank_rf_permutation"] = table["rf_f1_drop"].rank(ascending=False).astype(int)
    table["rank_rf_mdi"] = table["rf_mdi"].rank(ascending=False).astype(int)
    table["highlighted_by_paper"] = table["feature"].isin(PAPER_KEY_ATTRIBUTES)
    table = table.sort_values("rank_final")
    table.round(4).to_csv(tables_dir / "C_feature_importance.csv", index=False)

    # How well do the three rankings agree with each other?
    agree = pd.DataFrame(
        [
            ("permutation (best model) vs permutation (RF)",
             spearmanr(table["final_f1_drop"], table["rf_f1_drop"])[0]),
            ("permutation (best model) vs MDI (RF)", spearmanr(table["final_f1_drop"], table["rf_mdi"])[0]),
            ("permutation (RF) vs MDI (RF)", spearmanr(table["rf_f1_drop"], table["rf_mdi"])[0]),
        ],
        columns=["comparison", "spearman_rank_agreement"],
    )
    agree.round(4).to_csv(tables_dir / "C_ranking_agreement.csv", index=False)

    # Cross-check with Ma et al. (2024) Figs. 4-5.
    top4 = list(table.head(4)["feature"])
    cross = pd.DataFrame(
        [
            {
                "paper_attribute": f,
                "our_rank_best_model": int(table.loc[table["feature"] == f, "rank_final"].iloc[0]),
                "our_rank_rf": int(table.loc[table["feature"] == f, "rank_rf_permutation"].iloc[0]),
                "in_our_top4": f in top4,
            }
            for f in PAPER_KEY_ATTRIBUTES
        ]
    )
    cross.to_csv(tables_dir / "C_paper_crosscheck.csv", index=False)

    print("  C2. feature-subset curve", flush=True)
    curve, freq = feature_subset_curve(X, y, classes, feature_names, n_repeats)
    curve.round(4).to_csv(tables_dir / "C_feature_subset.csv", index=False)
    freq.round(2).to_csv(tables_dir / "C_selection_frequency.csv", index=False)

    plot_permutation(final_imp, rf_imp, final_model_name, figures_dir)
    plot_methods_and_direction(table, figures_dir)
    plot_subset_curve(curve, figures_dir)
    return table, agree, cross, curve
