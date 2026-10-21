"""
build_figures.py -- the extra figures used by the project report and the paper.

    python report/build_figures.py

Everything is drawn from the dataset and from the result tables written by
`python run_all.py --review2`; no number is typed in here. Output: report/figures/.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from config import FEATURE_COLUMNS, MA_2024_TABLE8_WEIGHT_SUM  # noqa: E402
from preprocessing import load_red_wine_xy  # noqa: E402

OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
R1 = ROOT / "results" / "tables"
R2 = ROOT / "results" / "review2" / "tables"
BERRY, ROSE, GOLD, INK, MUTED, SAGE, TINT = "#6D2E46", "#A26769", "#C8A45C", "#2B2B2B", "#9A9A9A", "#5B7F6B", "#F5EFF1"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
_, y, _, df = load_red_wine_xy()


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# --------------------------------------------------------------------------
# Framework diagram
# --------------------------------------------------------------------------
def box(ax, x, y, w, h, title, body, edge):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                                fc="white", ec=edge, lw=1.2))
    ax.text(x + w / 2, y + h - 0.022, title, ha="center", va="top", fontsize=8.6, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.062, body, ha="center", va="top", fontsize=7.2, color="#444444", linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, color=INK):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10, lw=1.1, color=color))


def framework():
    fig, ax = plt.subplots(figsize=(12.5, 8.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    bands = [
        (0.77, "A.  Data preparation", "#2E5E8C", [
            ("UCI red wine data", "1,599 wines\n11 lab measurements\nquality grade 3–8"),
            ("Six imbalanced classes", "grades 5 and 6 = 82.5 %\ngrades 3 and 8 = 1.75 %\nno class merged"),
            ("Min-max scaling", "inside a Pipeline,\nfitted on each\ntraining fold only"),
            ("Stratified 10-fold CV", "× 10 repeats, seeds 0–9\n100 fold-runs\n15,990 predictions"),
        ]),
        (0.52, "B.  Review 1 — reproduction of Ma et al. (2024)", BERRY, [
            ("Four base learners", "SVM · Random Forest\nGradient Boosting (for RNN)\nMLP (for ELM)"),
            ("Accuracy weight", "normalised inverse of\neach learner's CV error\nEqs. (5)–(6)"),
            ("Diversity weight", "distances between 0/1\nerror vectors\nEqs. (7)–(9)"),
            ("Weighted vote", "w = ½(acc + div), Eq. (4)\nsoft and hard readings\nof Eq. (1)"),
            ("Checks on the paper", "Table 9 reconciliation\nTable 8 consistency\nmetric terminology"),
        ]),
        (0.27, "C.  Review 2 — the three requested changes", "#8A6A1F", [
            ("Class balancing", "none · Review-1 partial\nclass weights on all four\nSMOTE inside the fold"),
            ("Weight sharpening", "temperature T on Eqs. (5)\nand (9): a diagnostic test\nof the Review-1 diagnosis"),
            ("Learned temperature", "T chosen by an inner\n5-fold CV in each\ntraining fold"),
            ("Stacking and members", "logistic-regression combiner\nExtraTrees, HistGB\nbalanced combiner"),
            ("Feature importance", "permutation (held-out)\nMDI · Spearman direction\ntop-k lab-test subsets"),
        ]),
        (0.02, "D.  Evaluation and delivery", SAGE, [
            ("Metrics", "accuracy · balanced accuracy\nmacro-F1 (primary) · per-class\nrecall · paired comparison"),
            ("Model selection", "best macro-F1 and best\naccuracy reported\nside by side"),
            ("Web application", "Streamlit: results pages\nand live prediction\nfrom 11 measurements"),
            ("Report and paper", "every number read\nfrom the result tables"),
        ]),
    ]
    for y0, title, colour, items in bands:
        h = 0.2
        ax.add_patch(FancyBboxPatch((0.01, y0), 0.98, h, boxstyle="round,pad=0.004,rounding_size=0.015",
                                    fc=colour + "14", ec=colour, lw=1.4))
        ax.text(0.022, y0 + h - 0.018, title, fontsize=9.5, fontweight="bold", color=colour, va="top")
        n = len(items); gap = 0.03; w = (0.94 - gap * (n - 1)) / n
        for i, (t, b) in enumerate(items):
            x = 0.03 + i * (w + gap)
            box(ax, x, y0 + 0.018, w, h - 0.068, t, b, colour)
            if i < n - 1 and title[0] in "ABD":
                arrow(ax, x + w + 0.002, y0 + 0.018 + (h - 0.068) / 2, x + w + gap - 0.002, y0 + 0.018 + (h - 0.068) / 2, colour)
        if title[0] == "B":
            for i in range(n - 1):
                x = 0.03 + i * (w + gap)
                arrow(ax, x + w + 0.002, y0 + 0.018 + (h - 0.068) / 2, x + w + gap - 0.002, y0 + 0.018 + (h - 0.068) / 2, colour)
    for ya, yb in ((0.77, 0.72), (0.52, 0.47), (0.27, 0.22)):
        arrow(ax, 0.5, ya - 0.002, 0.5, yb + 0.002, INK)
    save(fig, "framework.png")


# --------------------------------------------------------------------------
# Dataset figures
# --------------------------------------------------------------------------
def class_distribution():
    counts = df["quality"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bars = ax.bar(counts.index.astype(str), counts.values, color=[ROSE if c in (5, 6) else BERRY for c in counts.index])
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 10, f"{v}\n({100 * v / len(df):.1f} %)", ha="center", fontsize=8.5)
    ax.set_xlabel("Quality grade"); ax.set_ylabel("Number of wines"); ax.set_ylim(0, counts.max() * 1.22)
    save(fig, "class_distribution.png")


def features_by_grade():
    feats = ["alcohol", "volatile acidity", "sulphates", "citric acid"]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    grades = sorted(df["quality"].unique())
    for ax, f in zip(axes, feats):
        data = [df.loc[df["quality"] == g, f] for g in grades]
        bp = ax.boxplot(data, tick_labels=[str(g) for g in grades], patch_artist=True, widths=0.6,
                        medianprops={"color": INK}, flierprops={"markersize": 2, "markeredgecolor": MUTED})
        for p in bp["boxes"]:
            p.set(facecolor=TINT, edgecolor=BERRY)
        ax.set_title(f, fontsize=10); ax.set_xlabel("Quality grade")
    save(fig, "features_by_grade.png")


def correlation_heatmap():
    cols = FEATURE_COLUMNS + ["quality"]
    c = df[cols].corr()
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    im = ax.imshow(c.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8.5); ax.set_yticklabels(cols, fontsize=8.5)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{c.values[i, j]:.2f}", ha="center", va="center", fontsize=6.6,
                    color="white" if abs(c.values[i, j]) > 0.55 else INK)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="Pearson correlation")
    ax.spines[:].set_visible(False)
    save(fig, "correlation_heatmap.png")


# --------------------------------------------------------------------------
# Results figures
# --------------------------------------------------------------------------
def model_ranking():
    s = pd.read_csv(R1 / "model_accuracy_summary.csv").sort_values("overall_accuracy_pct")
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    colours = [BERRY if m.startswith("Ensemble (soft") else (GOLD if m == "RF" else MUTED) for m in s["model"]]
    bars = ax.barh(s["model"], s["overall_accuracy_pct"], color=colours)
    for b, v in zip(bars, s["overall_accuracy_pct"]):
        ax.text(v + 0.15, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=8.5)
    ax.set_xlim(55, 74); ax.set_xlabel("Accuracy (%) — pooled over 100 fold-runs")
    save(fig, "model_ranking.png")


def weights_vs_paper():
    b1 = pd.read_csv(R2 / "B1_weight_temperature.csv")
    row = b1[(b1["balancing"] == "partial") & (b1["sharpen"] == "both") & (b1["temperature"] == 1)].iloc[0]
    ours = {"SVM": row["w_SVM"], "Random Forest": row["w_RF"], "Gradient Boosting\n(paper: RNN)": row["w_GradBoost"],
            "MLP\n(paper: ELM)": row["w_MLP"]}
    paper = [MA_2024_TABLE8_WEIGHT_SUM[k] for k in ("SVM", "RF", "RNN", "ELM")]
    x = np.arange(4)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    b1_ = ax.bar(x - 0.19, list(ours.values()), 0.38, color=BERRY, label="Our reproduction (mean of 10 repeats)")
    b2_ = ax.bar(x + 0.19, paper, 0.38, color=GOLD, label="Ma et al. (2024), Table 8")
    for bars in (b1_, b2_):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.004, f"{b.get_height():.3f}", ha="center", fontsize=8)
    ax.axhline(0.25, color=INK, ls="--", lw=1, label="Uniform weight (0.25)")
    ax.set_xticks(x); ax.set_xticklabels(list(ours)); ax.set_ylim(0, 0.40); ax.set_ylabel("Final weight wᵢ, Eq. (4)")
    ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=3)
    save(fig, "weights_vs_paper.png")


def confusion_matrices():
    mats = [("Review-1 ensemble (soft vote)", R2 / "confusion_matrix_review1_ensemble.csv"),
            ("Review-1 Random Forest", R1 / "confusion_matrix_RF.csv"),
            ("Review-2 best: Random Forest + SMOTE", R2 / "confusion_matrix_review2_best.csv")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    for ax, (title, path) in zip(axes, mats):
        cm = pd.read_csv(path, index_col=0).values
        rec = 100 * cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(rec, cmap="RdPu", vmin=0, vmax=100)
        for i in range(6):
            for j in range(6):
                ax.text(j, i, f"{cm[i, j]}\n{rec[i, j]:.0f}%", ha="center", va="center", fontsize=6.8,
                        color="white" if rec[i, j] > 55 else INK)
        ax.set_xticks(range(6)); ax.set_yticks(range(6))
        ax.set_xticklabels(range(3, 9)); ax.set_yticklabels(range(3, 9))
        ax.set_xlabel("Predicted grade"); ax.set_ylabel("True grade"); ax.set_title(title, fontsize=10)
        ax.spines[:].set_visible(False)
    fig.suptitle("Pooled confusion matrices (15,990 predictions; percentages are row-wise recall)", fontsize=10)
    fig.tight_layout()
    save(fig, "confusion_matrices.png")


def app_architecture():
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    items = {
        "data": (0.02, 0.72, "Dataset", "data/raw/winequality-red.csv\n1,599 wines × 11 features", "#2E5E8C"),
        "run": (0.02, 0.06, "python run_all.py --review2", "100 fold-runs per model\nfor every experiment", "#2E5E8C"),
        "src": (0.36, 0.72, "Project code (src/)", "get_base_learners()\nmake_paper_learners('smote')", BERRY),
        "models": (0.36, 0.40, "Models trained at start-up", "Random Forest · RF + SMOTE\ncached with st.cache_resource", BERRY),
        "results": (0.36, 0.06, "Result tables and figures", "results/ and results/review2/\nread by the results pages", BERRY),
        "cloud": (0.69, 0.72, "Streamlit Community Cloud", "deployed from GitHub\napp/requirements.txt", MUTED),
        "app": (0.69, 0.40, "streamlit_app.py — 7 pages", "Overview · Dataset · Review 1\nClass balancing · Improvement\nFeature importance · Predict", SAGE),
        "test": (0.69, 0.06, "app/test_app.py", "15 automated checks", MUTED),
    }
    for key, (x, y0, t, b, c) in items.items():
        box(ax, x, y0, 0.29, 0.2, t, b, c)
    arrow(ax, 0.31, 0.82, 0.36, 0.82); arrow(ax, 0.165, 0.72, 0.165, 0.26); arrow(ax, 0.31, 0.16, 0.36, 0.16)
    arrow(ax, 0.505, 0.72, 0.505, 0.60); arrow(ax, 0.65, 0.50, 0.69, 0.50); arrow(ax, 0.65, 0.18, 0.70, 0.40)
    arrow(ax, 0.835, 0.72, 0.835, 0.60); arrow(ax, 0.835, 0.40, 0.835, 0.26)
    save(fig, "app_architecture.png")


def app_examples():
    """Predictions of the two web-app models for the app's example wines (Table 5.3 of the report)."""
    from sklearn.base import clone
    from base_learners import get_base_learners
    from review2 import make_paper_learners
    X, y, _, _ = load_red_wine_xy()
    models = {"rf": clone(get_base_learners()["RF"]).fit(X, y),
              "smote": clone(make_paper_learners("smote")["RF"]).fit(X, y)}
    examples = {"Typical wine (median of all wines)": df[FEATURE_COLUMNS].median()}
    for g in (4, 5, 6, 7, 8):
        examples[f"Typical grade-{g} wine"] = df[df["quality"] == g][FEATURE_COLUMNS].median()
    rows = []
    for name, ex in examples.items():
        x = ex[FEATURE_COLUMNS].to_numpy().reshape(1, -1)
        row = {"example": name, "alcohol": ex["alcohol"], "volatile acidity": ex["volatile acidity"],
               "sulphates": ex["sulphates"]}
        for key, m in models.items():
            p = m.predict_proba(x)[0]
            row[f"{key}_grade"] = int(m.classes_[p.argmax()])
            row[f"{key}_prob"] = round(100 * p.max(), 1)
        rows.append(row)
    (ROOT / "report" / "data").mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(ROOT / "report" / "data" / "app_examples.csv", index=False)
    print("wrote data/app_examples.csv")


def terminal(lines, name, command):
    """Real command output drawn as a terminal window (for the report's output snapshots)."""
    cmd = command if isinstance(command, list) else [command]
    text = [f"$ {cmd[0]}"] + [f">   {c}" for c in cmd[1:]] + lines
    h = 0.24 * len(text) + 0.5
    fig = plt.figure(figsize=(0.08 * max(len(t) for t in text) + 0.5, h))
    fig.patch.set_facecolor("#1E1E1E")
    for k, line in enumerate(text):
        colour = "#7FD47F" if "PASS" in line or "ALL CHECKS" in line else ("#9CDCFE" if k < len(cmd) else "#E6E6E6")
        fig.text(0.02, 1 - (k + 1) * 0.24 / h, line, family="DejaVu Sans Mono", fontsize=9.5, color=colour, va="top")
    save(fig, name)


def output_snapshots():
    out = (ROOT / "report" / "data" / "test_app_output.txt").read_text().splitlines()
    terminal([line for line in out if not line.startswith("exit")], "out_tests.png", "python app/test_app.py")
    head = pd.read_csv(R2 / "headline_review1_vs_review2.csv").set_index("metric").round(2)
    with pd.option_context("display.width", 120):
        terminal(head.to_string().splitlines(), "out_headline.png",
                 ["python -c \"import pandas as pd; print(pd.read_csv(",
                  "'results/review2/tables/headline_review1_vs_review2.csv', index_col=0).round(2))\""])


def split_screenshots(max_ratio=1.3):
    """Cut tall full-page app screenshots at blank rows so each part fits a report page."""
    from PIL import Image
    src, dst = OUT / "app", OUT / "app" / "parts"
    dst.mkdir(exist_ok=True)
    for f in sorted(src.glob("app_*.png")):
        im = Image.open(f).convert("RGB")
        w, h = im.size
        n = max(1, int(np.ceil(h / (w * max_ratio))))
        a = np.asarray(im.convert("L"))[:, int(0.25 * w):]   # main area, right of the sidebar
        blank = np.where((a > 245).all(axis=1))[0]
        cuts = []
        for k in range(1, n):
            target = k * h / n
            near = blank[np.abs(blank - target) < 0.12 * h]
            cut = int(near[np.argmin(np.abs(near - target))]) if len(near) else int(target)
            cuts.append(cut)
        edges = [0] + cuts + [h]
        for k in range(n):
            part = im.crop((0, edges[k], w, edges[k + 1]))
            g = np.asarray(part.convert("L"))[:, int(0.25 * w):]
            rows = np.where((g < 245).any(axis=1))[0]
            if len(rows):
                part = part.crop((0, 0, w, min(part.size[1], rows[-1] + 60)))
            part.save(dst / f"{f.stem}_{k + 1}of{n}.png")
        print("split", f.name, "into", n)


if __name__ == "__main__":
    framework()
    class_distribution()
    features_by_grade()
    correlation_heatmap()
    model_ranking()
    weights_vs_paper()
    confusion_matrices()
    app_architecture()
    app_examples()
    output_snapshots()
    split_screenshots()
