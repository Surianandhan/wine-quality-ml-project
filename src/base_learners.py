"""
base_learners.py

Individual base-learner definitions and 10-fold cross-validation, standing in
for the four base learners of Ma et al. (2024): SVM, RNN, ELM, and Random
Forest.

SUBSTITUTIONS (classical-ML-only university syllabus -- no deep learning
beyond a standard backprop MLP, no non-backprop training paradigms):

  - RNN (recurrent neural network; a deep-learning sequence model) is replaced
    with GradientBoostingClassifier. Both sit outside the "single flat model"
    mold of the original ensemble: gradient boosting fits each new tree to the
    residual errors of the trees before it, which is a classical-ML way of
    letting the model refine itself round over round -- the closest in-syllabus
    analogue to the RNN's iterative refinement, without backprop-through-time
    or exploding/vanishing-gradient machinery. (The project brief permits
    "AdaBoostClassifier / GradientBoostingClassifier"; we use gradient boosting
    because AdaBoost's default depth-1 stumps perform poorly on this 6-class
    imbalanced problem.)
  - ELM (extreme learning machine; random, fixed hidden-layer weights with a
    closed-form linear output layer, i.e. explicitly *not* trained with
    backprop) is replaced with MLPClassifier. An MLP is the closest classical
    analogue that is still a neural network, but -- unlike ELM -- all of its
    weights (hidden and output) are learned via standard backpropagation,
    which is what the syllabus covers.
  - SVM and Random Forest are kept as-is: both are already classical ML and
    directly available in scikit-learn.

PREPROCESSING NOTE (important): every learner is wrapped in a Pipeline whose
first step is MinMaxScaler. This keeps the paper's min-max normalization step
(Fig. 2) while ensuring the scaler is fit on the *training fold only* during
cross-validation. Scaling the full dataset once before CV -- as an earlier
version of this project did -- leaks test-fold information into the scaling
constants and inflates the reported scores.

CLASS IMBALANCE: quality classes 3 and 8 have only 10 and 18 samples out of
1599. SVM and RF therefore use balanced class weights so the minority classes
contribute to the loss instead of being ignored outright. This is a modelling
choice we make explicitly; the paper does not state any imbalance handling.
"""
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from config import N_SPLITS, RANDOM_STATE


def _pipe(estimator):
    """Min-max scaling fit inside each CV fold, then the estimator."""
    return Pipeline([("scaler", MinMaxScaler()), ("clf", estimator)])


def get_base_learners(random_state=RANDOM_STATE):
    """Return the four base learners, keyed by name, each as a scaling pipeline.

    Keys "MLP" and "GradBoost" stand in for the paper's "ELM" and "RNN"
    respectively -- see module docstring for why.
    """
    return {
        # The soft-vote ensemble (Eq. 1) needs probability estimates, which an
        # SVM does not produce natively. SVC(probability=True) would supply them,
        # but it refits an internal 5-fold Platt calibration whose result can
        # disagree with the model's own decision_function. Wrapping in
        # CalibratedClassifierCV makes that calibration step explicit and keeps
        # it inside the CV fold. (Both routes use Platt scaling; this is a
        # transparency choice, not a deprecation -- SVC(probability=True) is
        # still perfectly valid.)
        "SVM": _pipe(
            CalibratedClassifierCV(
                SVC(
                    kernel="rbf",
                    C=10.0,
                    gamma="scale",
                    class_weight="balanced",
                    random_state=random_state,
                ),
                ensemble=False,
            )
        ),
        "RF": _pipe(
            RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced_subsample",
                random_state=random_state,
            )
        ),
        "MLP": _pipe(
            MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=2000,
                # No early_stopping: it would carve a 10% validation slice out
                # of a training set containing as few as 9 class-3 samples.
                random_state=random_state,
            )
        ),
        "GradBoost": _pipe(
            GradientBoostingClassifier(
                n_estimators=200,
                random_state=random_state,
            )
        ),
    }


def cross_val_predictions(X, y, n_splits=N_SPLITS, random_state=RANDOM_STATE):
    """Out-of-fold predictions for each base learner under one shared
    stratified k-fold split (so every learner is scored on the same folds)."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    learners = get_base_learners(random_state)
    return {
        name: cross_val_predict(model, X, y, cv=skf, n_jobs=-1)
        for name, model in learners.items()
    }


def cross_val_accuracy_scores(X, y, n_splits=N_SPLITS, random_state=RANDOM_STATE):
    """Per-fold accuracy scores for each base learner (for the mean/std
    summary reported alongside the pooled confusion-matrix metrics)."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    learners = get_base_learners(random_state)
    return {
        name: cross_val_score(model, X, y, cv=skf, scoring="accuracy", n_jobs=-1)
        for name, model in learners.items()
    }


if __name__ == "__main__":
    from preprocessing import load_red_wine_xy

    X, y, feature_columns, _ = load_red_wine_xy()
    scores = cross_val_accuracy_scores(X, y)
    for name, folds in scores.items():
        print(f"{name}: mean accuracy = {folds.mean():.4f} (+/- {folds.std():.4f}) over {len(folds)} folds")
