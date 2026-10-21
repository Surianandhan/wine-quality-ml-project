"""
ensemble.py

The weighted ensemble of Ma et al. (2024), Section 3.3.3 / Eqs. (1)-(9):

  y_hat   = sum_i w_i * y_hat_i                                        (1)
  w_i     = 0.5 * (w_accuracy_i + w_diversity_i)                       (4)
  w_accuracy_i  = (eps_i_CV)^-1 / sum_j (eps_j_CV)^-1                  (5)
  eps_i_CV      = mean 0/1 CV error of learner i over all folds        (6)
  e_i           = per-sample 0/1 error vector of learner i (Eq. 7)
  D_i           = sum_{j != i} || e_i - e_j ||                        (8)
  w_diversity_i = D_i / sum_j D_j                                      (9)

HOW Eq. (1) IS REALIZED -- and why it matters
---------------------------------------------
Eq. (1) is a weighted *sum* of each learner's output, y_hat = sum_i w_i y_hat_i.
There are two ways to read y_hat_i for a classifier, and they give materially
different results:

  SOFT vote (used for our headline result): y_hat_i is the per-class
    probability vector P_i from predict_proba. The ensemble output is the
    weighted sum of those vectors, P = sum_i w_i * P_i, and the prediction is
    argmax(P). This is the literal reading of Eq. (1) -- an actual weighted sum
    of scores -- and it lets a confident strong learner outweigh several
    unconfident weak ones.

  HARD vote (kept for comparison): y_hat_i is the one-hot encoded predicted
    label, so the "sum" degenerates into weighted majority voting. On this
    imbalanced 6-class problem it lets three weaker learners jointly outvote
    the strongest one, and measurably underperforms the soft vote.

Both are computed and reported, since the difference between them is a genuine
finding about how the paper's formula should be interpreted.

Evaluation protocol: 10-fold CV repeated 10 times (100 total fold-runs),
matching the paper's "10 runs of 10-fold cross-validation" (Section 3.4).
"""
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from base_learners import get_base_learners
from config import N_REPEATS, N_SPLITS


def _error_vector(y_true, y_pred):
    """g(y_hat, y) from Eq. (3): 0 if correct, 1 if wrong."""
    return (np.asarray(y_true) != np.asarray(y_pred)).astype(float)


def compute_weights(error_vectors):
    """error_vectors: dict[name] -> 0/1 error array of length N (Eq. 7).

    Returns (w, w_accuracy, w_diversity, cv_errors), each a dict[name] -> float,
    following Eqs. (4), (5), (8), (9).
    """
    names = list(error_vectors.keys())
    cv_errors = {name: float(error_vectors[name].mean()) for name in names}  # Eq. (6)

    # Eq. (5): accuracy-based weight. A learner with zero CV error would
    # divide by zero; fall back to a large-but-finite inverse error instead
    # (equivalent to treating it as "as good as effectively perfect").
    inv_err = {name: (1.0 / cv_errors[name] if cv_errors[name] > 0 else 1e6) for name in names}
    total_inv = sum(inv_err.values())
    w_accuracy = {name: inv_err[name] / total_inv for name in names}

    # Eq. (8): diversity = sum of Euclidean distances to every other learner's
    # error vector.
    D = {}
    for name in names:
        D[name] = sum(
            np.linalg.norm(error_vectors[name] - error_vectors[other])
            for other in names
            if other != name
        )
    total_D = sum(D.values())
    w_diversity = {name: D[name] / total_D for name in names}  # Eq. (9)

    w = {name: 0.5 * (w_accuracy[name] + w_diversity[name]) for name in names}  # Eq. (4)
    return w, w_accuracy, w_diversity, cv_errors


def weight_concentration(weights):
    """How far the paper's weights depart from a plain uniform average.

    This matters for interpreting the reproduction. Eqs. (5) and (9) normalize
    inverse-errors and pairwise error distances, and both are only weakly
    discriminative when the base learners have broadly similar error rates: a
    learner with 29% error and one with 37% error receive weights of roughly
    0.27 and 0.21. The paper's own Table 8 shows the same near-uniform pattern
    (0.2516 / 0.2286 / 0.2168 / 0.3030 against a uniform 0.25).

    With weights this flat, the ensemble is close to an unweighted average of
    its members, and an average of one strong learner and three weaker ones
    lands *between* them rather than above the strongest. Reported as a
    diagnostic so this can be checked rather than asserted.

    Returns dict with the uniform baseline, max/min weight, spread, and the
    max absolute deviation from uniform.
    """
    values = np.array(list(weights.values()), dtype=float)
    uniform = 1.0 / len(values)
    return {
        "n_learners": len(values),
        "uniform_weight": uniform,
        "max_weight": float(values.max()),
        "min_weight": float(values.min()),
        "weight_spread": float(values.max() - values.min()),
        "max_abs_deviation_from_uniform": float(np.abs(values - uniform).max()),
    }


def weighted_vote(preds, weights, classes):
    """HARD-vote realization of Eq. (1): each learner one-hot votes its predicted
    label with weight w_i. Kept for comparison against the soft vote."""
    names = list(preds.keys())
    n_samples = len(next(iter(preds.values())))
    class_index = {c: i for i, c in enumerate(classes)}
    votes = np.zeros((n_samples, len(classes)))
    for name in names:
        w = weights[name]
        idx = np.array([class_index[p] for p in preds[name]])
        votes[np.arange(n_samples), idx] += w
    return np.array([classes[i] for i in votes.argmax(axis=1)])


def weighted_soft_vote(probas, weights, classes):
    """SOFT-vote realization of Eq. (1) -- the literal weighted sum of scores.

    probas: dict[name] -> (n_samples, n_classes) predict_proba matrix, with
    columns ordered to match `classes`. Computes P = sum_i w_i * P_i and
    returns argmax(P) as a class label.
    """
    names = list(probas.keys())
    weighted_sum = np.zeros_like(next(iter(probas.values())), dtype=float)
    for name in names:
        weighted_sum += weights[name] * probas[name]
    classes_arr = np.asarray(classes)
    return classes_arr[weighted_sum.argmax(axis=1)]


def _align_proba_columns(proba, model_classes, classes):
    """Reorder/pad a predict_proba matrix so its columns match `classes`.

    A learner trained on a fold that happens to contain no samples of some rare
    class will return fewer columns; those classes get probability 0.
    """
    model_classes = list(model_classes)
    if model_classes == list(classes):
        return proba
    aligned = np.zeros((proba.shape[0], len(classes)))
    for j, cls in enumerate(model_classes):
        aligned[:, classes.index(cls)] = proba[:, j]
    return aligned


def run_repeated_cv(X, y, n_splits=N_SPLITS, n_repeats=N_REPEATS, base_seed=0):
    """Run n_repeats independent n_splits-fold stratified CVs (matching the
    paper's 10-fold CV x 10 repeats = 100 total fold-runs).

    Within each repeat, every base learner is scored on the *same* fold split
    (required for D_i in Eq. 8 to compare error vectors sample-for-sample),
    the paper's weights are computed from that repeat's out-of-fold errors,
    and the weighted-vote ensemble prediction is formed for that repeat.

    Returns a dict with:
      - "classes": sorted list of class labels
      - "per_repeat": list of per-repeat weight/accuracy records
      - "pooled_true": concatenation of y across all repeats
      - "pooled_preds": dict[learner] -> concatenation of out-of-fold preds
      - "pooled_ensemble": concatenation of ensemble preds across all repeats
      - "weights_df_records": flat list of dicts, one per repeat, for a
        weights-over-repeats table
    """
    classes = sorted(np.unique(y).tolist())
    learners = get_base_learners()

    per_repeat = []
    weights_df_records = []
    pooled_true = []
    pooled_preds = {name: [] for name in learners}
    pooled_ensemble = []       # soft vote -- the headline ensemble
    pooled_ensemble_hard = []  # hard vote -- kept for comparison

    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=base_seed + r)

        fold_preds = {}
        fold_probas = {}
        for name, model in learners.items():
            proba = cross_val_predict(model, X, y, cv=skf, n_jobs=-1, method="predict_proba")
            fold_probas[name] = _align_proba_columns(proba, classes, classes)
            # Derive the hard label from the same probabilities, so the two
            # voting schemes are compared on identical fitted models.
            fold_preds[name] = np.asarray(classes)[proba.argmax(axis=1)]

        error_vectors = {name: _error_vector(y, fold_preds[name]) for name in learners}
        w, w_acc, w_div, cv_err = compute_weights(error_vectors)

        ensemble_pred = weighted_soft_vote(fold_probas, w, classes)
        ensemble_pred_hard = weighted_vote(fold_preds, w, classes)

        accuracy = {name: float((fold_preds[name] == y).mean()) for name in learners}
        accuracy["Ensemble"] = float((ensemble_pred == y).mean())
        accuracy["Ensemble_hard_vote"] = float((ensemble_pred_hard == y).mean())

        per_repeat.append(
            {
                "repeat": r,
                "weights": w,
                "weights_accuracy": w_acc,
                "weights_diversity": w_div,
                "cv_error": cv_err,
                "accuracy": accuracy,
            }
        )
        weights_df_records.append({"repeat": r, **{f"w_{name}": w[name] for name in learners}})

        pooled_true.append(y)
        for name in learners:
            pooled_preds[name].append(fold_preds[name])
        pooled_ensemble.append(ensemble_pred)
        pooled_ensemble_hard.append(ensemble_pred_hard)

    pooled_true = np.concatenate(pooled_true)
    pooled_preds = {name: np.concatenate(v) for name, v in pooled_preds.items()}
    pooled_ensemble = np.concatenate(pooled_ensemble)
    pooled_ensemble_hard = np.concatenate(pooled_ensemble_hard)

    return {
        "classes": classes,
        "per_repeat": per_repeat,
        "weights_df_records": weights_df_records,
        "pooled_true": pooled_true,
        "pooled_preds": pooled_preds,
        "pooled_ensemble": pooled_ensemble,
        "pooled_ensemble_hard": pooled_ensemble_hard,
    }


if __name__ == "__main__":
    from preprocessing import load_red_wine_xy

    X, y, feature_columns, _ = load_red_wine_xy()
    results = run_repeated_cv(X, y, n_repeats=2)  # quick smoke test, 2 repeats only

    for name in list(results["pooled_preds"].keys()):
        acc = (results["pooled_preds"][name] == results["pooled_true"]).mean()
        print(f"{name}: pooled accuracy over {len(results['per_repeat'])} repeats = {acc:.4f}")
    soft_acc = (results["pooled_ensemble"] == results["pooled_true"]).mean()
    hard_acc = (results["pooled_ensemble_hard"] == results["pooled_true"]).mean()
    print(f"Ensemble (soft vote): pooled accuracy = {soft_acc:.4f}")
    print(f"Ensemble (hard vote): pooled accuracy = {hard_acc:.4f}")
    print("\nWeights, repeat 0:", results["per_repeat"][0]["weights"])
