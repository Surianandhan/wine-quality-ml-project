"""
results.py -- every number the report and the paper quote, read from the
project's result files. Nothing here is typed in by hand except the base
paper's published values, which come from src/config.py.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import config as C  # noqa: E402

T1 = ROOT / "results" / "tables"
T2 = ROOT / "results" / "review2" / "tables"
F1 = ROOT / "results" / "figures"
F2 = ROOT / "results" / "review2" / "figures"
FIG = ROOT / "report" / "figures"
DATA = ROOT / "report" / "data"

# Links of the deployed application and the repository. Filled in after deployment.
APP_URL = None
REPO_URL = "https://github.com/Surianandhan/wine-quality-ml-project"

CLASSES = [3, 4, 5, 6, 7, 8]
FEATURES = C.FEATURE_COLUMNS


def f2(x):
    return f"{float(x):.2f}"


def pct(x, d=2):
    return f"{x:.{d}f} %"


# ---------------- dataset ----------------
wine = pd.read_csv(C.RED_WINE_CSV, sep=";")
N = len(wine)
class_counts = wine["quality"].value_counts().sort_index()
n_duplicates = int(wine.duplicated().sum())
pearson = wine[FEATURES].corrwith(wine["quality"])
spearman = wine[FEATURES].corrwith(wine["quality"], method="spearman")
desc = wine[FEATURES].describe().T

# ---------------- Review 1 ----------------
summary = pd.read_csv(T1 / "model_accuracy_summary.csv").set_index("model")["overall_accuracy_pct"]
acc = {k: float(v) for k, v in summary.items()}
bench = pd.read_csv(T1 / "benchmark_comparison.csv").set_index("class")
t9 = pd.to_numeric(pd.read_csv(T1 / "paper_table9_reconciliation.csv").set_index("quantity")["value"], errors="coerce")
cons = pd.read_csv(T1 / "paper_internal_consistency_check.csv").set_index("quantity")["value"]
t9_class = pd.read_csv(T1 / "paper_table9_per_class_check.csv")
metrics = {m: pd.read_csv(T1 / f"metrics_{m}.csv").set_index("class")
           for m in ("Ensemble", "Ensemble_hard_vote", "RF", "SVM", "MLP", "GradBoost")}

# ---------------- Review 2 ----------------
comp = pd.read_csv(T2 / "model_comparison.csv")
balancing = pd.read_csv(T2 / "A_class_balancing.csv")
temp = pd.read_csv(T2 / "B1_weight_temperature.csv")
chosen = pd.read_csv(T2 / "B4_chosen_temperatures.csv")
improve = pd.read_csv(T2 / "B2_B3_improvements.csv").set_index("model")
paired = pd.read_csv(T2 / "paired_comparison.csv")
imp = pd.read_csv(T2 / "C_feature_importance.csv")
subset = pd.read_csv(T2 / "C_feature_subset.csv")
agree = pd.read_csv(T2 / "C_ranking_agreement.csv").set_index("comparison")["spearman_rank_agreement"]
headline = pd.read_csv(T2 / "headline_review1_vs_review2.csv").set_index("metric")
best_name = (T2 / "headline_best_model.txt").read_text().strip()

row1 = temp[(temp["balancing"] == "partial") & (temp["sharpen"] == "both") & (temp["temperature"] == 1)].iloc[0]
our_weights = {"SVM": row1["w_SVM"], "RF": row1["w_RF"], "GradBoost": row1["w_GradBoost"], "MLP": row1["w_MLP"]}


def cm(name):
    c = comp.set_index("model")
    return c.loc[name]


ENS_R1 = "Ensemble (paper weights) | Review 1 (SVM + RF only)"
ENS_SMOTE = "Ensemble (paper weights) | SMOTE oversampling"
ENS_CW = "Ensemble (paper weights) | Class weights, all four"
LT_R1 = "Learned-temperature ensemble | Review 1 (SVM + RF only)"
LT_SMOTE = "Learned-temperature ensemble | SMOTE oversampling"
RF_R1 = "RF | Review 1 (SVM + RF only)"
RF_SMOTE = "RF | SMOTE oversampling"
STACK4 = "Stacked: paper's 4 learners (class-weighted)"
STACK_BAL = "Stacked: paper's 4 learners, balanced combiner"
STACK_STRONG = "Stacked: SVM + RF + ExtraTrees + HistGB"
PAPER_STRONG = "Paper weights: SVM + RF + ExtraTrees + HistGB"


def share_sharp(balancing_name, t_min=10):
    sub = chosen[chosen["balancing"] == balancing_name]
    return 100 * (sub["temperature"] >= t_min).mean(), sub


def nice_model(name):
    """Readable model names for tables."""
    rep = {
        "Ensemble (paper weights)": "Paper ensemble",
        "Learned-temperature ensemble": "Learned-T ensemble",
        "Review 1 (SVM + RF only)": "Review-1 setup",
        "SMOTE oversampling": "SMOTE",
        "Class weights, all four": "class weights (all four)",
        "No balancing": "no balancing",
        "GradBoost": "Gradient Boosting",
        "RF": "Random Forest",
    }
    parts = [p.strip() for p in name.split("|")]
    parts = [rep.get(p, p) for p in parts]
    return " · ".join(parts)
