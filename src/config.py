"""
config.py

Single source of truth for paths, experiment settings, and the published
benchmark numbers we compare against. Previously these constants were
duplicated across evaluate.py and novelty_cluster_mine_feedback.py.
"""
from pathlib import Path

# --- Paths ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
RED_WINE_CSV = DATA_RAW_DIR / "winequality-red.csv"
WHITE_WINE_CSV = DATA_RAW_DIR / "winequality-white.csv"

RESULTS_DIR = PROJECT_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"

# Reduced-protocol runs (run_all.py --quick) write here instead of results/, so
# a fast sanity pass can never overwrite the canonical 10-repeat numbers that
# README.md and report/methodology.md quote. Gitignored.
QUICK_OUTPUT_DIR = PROJECT_ROOT / "results" / "_quick_run"

# Review 2 (class balancing, improvements, feature importance) writes to its own
# folder so the Review-1 reproduction numbers in results/tables/ stay
# byte-identical and can always be quoted as the baseline.
REVIEW2_DIR = RESULTS_DIR / "review2"
REVIEW2_TABLES_DIR = REVIEW2_DIR / "tables"
REVIEW2_FIGURES_DIR = REVIEW2_DIR / "figures"
QUICK_REVIEW2_DIR = QUICK_OUTPUT_DIR / "review2"

# --- Dataset --------------------------------------------------------------
FEATURE_COLUMNS = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
]
TARGET_COLUMN = "quality"

# --- Experiment protocol --------------------------------------------------
RANDOM_STATE = 42
N_SPLITS = 10       # 10-fold cross-validation
N_REPEATS = 10      # x 10 runs  => 100 experiments, as in Ma et al. (2024) Sec. 3.4
QUICK_N_REPEATS = 2  # used by run_all.py --quick for a fast sanity pass

# --- Published benchmark numbers (context only, not our results) ----------
# Classes 0,1,2,9,10 are always empty in this dataset and are omitted, exactly
# as Ma et al. (2024) omit them from their Tables 4-9.
BENCHMARK_CLASSES = [3, 4, 5, 6, 7, 8]
CORTEZ_2009_PER_CLASS_PRECISION = [0.00, 20.00, 67.50, 57.70, 58.60, 0.00]
MA_2024_PER_CLASS_PRECISION = [33.33, 63.16, 84.80, 88.06, 77.08, 50.00]
MA_2024_OVERALL_ACCURACY = 89.73

# Ma et al. (2024) Table 9 -- the ensemble confusion matrix, transcribed by eye
# from the printed table. Rows = prognostic (predicted) class, columns = actual
# class, both ordered [3, 4, 5, 6, 7, 8].
#
# CAVEAT: transcribed visually from the PDF and may contain reading errors.
# evaluate.paper_table9_reconciliation() uses this only to sanity-check the
# paper's reported figures against its own printed table; any conclusion drawn
# from it is stated as "could not reconcile", never as "the paper is wrong".
MA_2024_TABLE9_CONFUSION = [
    [1, 1, 1, 0, 0, 0],
    [0, 12, 6, 4, 0, 0],
    [2, 6, 173, 7, 11, 0],
    [0, 0, 14, 177, 11, 0],
    [0, 0, 10, 12, 37, 2],
    [0, 0, 0, 0, 1, 3],
]

# Range of overall accuracy commonly reported in the literature for the 6-class
# UCI red wine task, used for context in the report.
#
# CAVEAT: this band is an informal impression from the literature survey, NOT a
# figure compiled from a citation table. It is quoted as "typically reported"
# rather than as an established result, and tightening it with explicit
# citations is listed as future work. Do not present it as a sourced statistic.
LITERATURE_ACCURACY_RANGE_PCT = (62.0, 72.0)

# Ma et al. (2024) Figs. 4-5: the physicochemical attributes the paper singles
# out as most important. Review 2's feature-importance analysis is checked
# against this list.
PAPER_KEY_ATTRIBUTES = ["alcohol", "sulphates", "volatile acidity", "citric acid"]

# --- Review 2 settings ----------------------------------------------------
# PRIMARY METRIC, fixed before any Review-2 experiment was run.
# Accuracy rewards predicting the two majority classes (5 and 6 are 82.5% of the
# data) and is precisely what class balancing trades away to rescue the rare
# classes. Macro-F1 averages F1 over all six quality classes with equal weight,
# so it is the metric class balancing is meant to improve. Accuracy is still
# reported everywhere, for comparability with the paper.
REVIEW2_PRIMARY_METRIC = "macro_f1"

# SMOTE neighbours. The rarest class (3) has 10 samples, so a 10-fold training
# split holds 9 and a stacking inner split about 7 -- both enough for k = 5.
SMOTE_K_NEIGHBORS = 5

# Temperatures for the weight-sharpening test of the Review-1 diagnosis.
# T = 1 is the paper's Eqs. (5) and (9) exactly. Capped at 100 so the powers
# stay finite in float64.
WEIGHT_TEMPERATURES = [1, 2, 5, 10, 25, 100]

# Feature-subset sizes for the "how many lab tests do you need?" experiment.
FEATURE_SUBSET_SIZES = [1, 2, 3, 4, 6, 8, 11]

# Permutations per feature per fold for permutation importance.
PERMUTATION_REPEATS = 20

# Ma et al. (2024) Tables 4-7: overall accuracy of each individual base learner.
MA_2024_BASE_LEARNER_ACCURACY = {
    "SVM": 67.30,
    "RNN": 61.43,
    "ELM": 55.77,
    "RF": 80.71,
}

# Ma et al. (2024) Table 8: the final "weight-sum" w_i per base learner,
# i.e. Eq. (4)'s 0.5 * (w_accuracy + w_diversity). Note how close these are to
# a uniform 0.25 -- see evaluate.paper_internal_consistency_check().
MA_2024_TABLE8_WEIGHT_SUM = {
    "SVM": 0.2516,
    "RNN": 0.2286,
    "ELM": 0.2168,
    "RF": 0.3030,
}
