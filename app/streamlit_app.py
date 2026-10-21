"""
streamlit_app.py -- web front end for the wine-quality project.

    streamlit run app/streamlit_app.py

Everything shown comes from the project itself: the result pages read the CSVs
and figures that `python run_all.py --review2` writes, and the prediction page
trains its models with the project's own learner definitions
(base_learners.get_base_learners and review2.make_paper_learners), so the app
can never drift from the results in the report.
"""
import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.base import clone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from base_learners import get_base_learners  # noqa: E402
from config import FEATURE_COLUMNS  # noqa: E402
from preprocessing import load_red_wine_xy  # noqa: E402
from review2 import make_paper_learners  # noqa: E402

R1_TABLES = ROOT / "results" / "tables"
R1_FIGS = ROOT / "results" / "figures"
R2_TABLES = ROOT / "results" / "review2" / "tables"
R2_FIGS = ROOT / "results" / "review2" / "figures"
BERRY, GOLD, MUTED = "#6D2E46", "#C8A45C", "#9A9A9A"

MODELS = {
    "Random Forest": "Review-1 configuration: class-weighted Random Forest. The most "
                                     "accurate model in the project (71.03 % under 10 x 10 cross-validation).",
    "Random Forest + SMOTE": "Review-2 winner on macro-F1 (40.92): the same forest trained "
                                                    "on SMOTE-balanced data, so it calls rare grades more readily.",
}

st.set_page_config(page_title="Wine Quality Prediction", layout="wide")


# --------------------------------------------------------------------------
# Data and models (cached so they are built once per session)
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    X, y, feats, df = load_red_wine_xy()
    return df


@st.cache_data
def table(path):
    return pd.read_csv(path)


@st.cache_resource
def trained_models():
    """Fit both models on all 1,599 wines with the project's own settings."""
    X, y, _, _ = load_red_wine_xy()
    rf = clone(get_base_learners()["RF"]).fit(X, y)
    rf_smote = clone(make_paper_learners("smote")["RF"]).fit(X, y)
    return {list(MODELS)[0]: rf, list(MODELS)[1]: rf_smote}


def r1(name):
    return table(R1_TABLES / name)


def r2(name):
    return table(R2_TABLES / name)


def figure(path, caption):
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.warning(f"Figure not found: {path.name}. Run `python run_all.py --review2` first.")


def short(name):
    return (name.replace("Ensemble (paper weights) | ", "Paper ensemble · ")
            .replace("Learned-temperature ensemble | ", "Learned-T ensemble · ")
            .replace("Review 1 (SVM + RF only)", "Review-1 setup")
            .replace("Class weights, all four", "class weights")
            .replace("SMOTE oversampling", "SMOTE").replace("No balancing", "no balancing")
            .replace(" | ", " · "))


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def page_overview():
    st.title("Wine Quality Prediction Using a Weighted Ensemble")
    st.caption("A reproduction of Ma et al. (2024), *Journal of Business Research* 176:114576, extended with "
               "class balancing, an improved weighting scheme and feature importance.  "
               "Surianandhan S · 127018060 · CSE425 Machine Learning Essentials · SASTRA Deemed to be University")

    head = r2("headline_review1_vs_review2.csv").set_index("metric")
    summary = r1("model_accuracy_summary.csv").set_index("model")
    lt = r2("model_comparison.csv").set_index("model").loc["Learned-temperature ensemble | Review 1 (SVM + RF only)"]

    c = st.columns(4)
    c[0].metric("Paper's reported accuracy", "89.73 %")
    c[1].metric("Our faithful reproduction", f"{summary.loc['Ensemble (soft vote)', 'overall_accuracy_pct']:.2f} %")
    c[2].metric("Ensemble with learned weights", f"{lt['accuracy']:.2f} %",
                f"{lt['accuracy'] - summary.loc['Ensemble (soft vote)', 'overall_accuracy_pct']:+.2f} pts")
    c[3].metric("Best macro-F1 (all six grades)", f"{head.loc['macro_f1', 'review2_best']:.2f}",
                f"{head.loc['macro_f1', 'change_vs_review1_ensemble']:+.2f} pts")

    st.markdown(
        """
**The task.** Predict a red wine's sensory quality grade (3–8, scored by a tasting panel) from 11 routine
laboratory measurements, using the 1,599 wines of the UCI Wine Quality (red) dataset.

**Review 1 — reproduction.** The paper's weighted ensemble (SVM, Random Forest and two neural/boosting
learners combined with accuracy-and-diversity weights) was re-implemented exactly and evaluated with
stratified 10-fold cross-validation repeated 10 times. It reaches 69.01 %, not the reported 89.73 %, and three
checks on the paper's own tables explain why.

**Review 2 — the three requested changes.**
* **Class balancing** — four schemes compared; SMOTE gives the best macro-F1 and lifts recall on the rare grades.
* **Improving the result** — the paper's weights are nearly uniform; learning a sharper weighting inside each
  training fold lifts the ensemble from 69.01 % to 70.89 % and lets it draw level with Random Forest.
* **Feature importance** — alcohol, sulphates and volatile acidity drive the prediction; four lab tests carry
  most of the predictive value.

Use the menu on the left to explore each part, or go straight to **Predict a wine**.
        """
    )


def page_dataset():
    st.title("The dataset")
    df = load_data()
    st.write(f"**{len(df):,} red wines**, **{len(FEATURE_COLUMNS)} physicochemical measurements** and one target: "
             "the median quality grade given by at least three assessors (Cortez et al., 2009).")

    counts = df["quality"].value_counts().sort_index().rename_axis("quality").reset_index(name="wines")
    counts["share"] = (100 * counts["wines"] / counts["wines"].sum()).round(1)
    left, right = st.columns([3, 2])
    with left:
        chart = alt.Chart(counts).mark_bar(color=BERRY).encode(
            x=alt.X("quality:O", title="Quality grade", axis=alt.Axis(labelAngle=0)), y=alt.Y("wines:Q", title="Number of wines"),
            tooltip=["quality", "wines", "share"])
        st.altair_chart(chart + chart.mark_text(dy=-8).encode(text="wines:Q"), width="stretch")
    with right:
        st.dataframe(counts, hide_index=True, width="stretch")
        st.info("Grades 5 and 6 hold 82.5 % of the wines; grades 3 and 8 together hold 1.75 %. "
                "This imbalance is why Review 2 focuses on class balancing and macro-F1.")

    st.subheader("Summary statistics")
    st.dataframe(df[FEATURE_COLUMNS].describe().T.round(3), width="stretch")

    st.subheader("Correlation with quality")
    rho = df[FEATURE_COLUMNS].corrwith(df["quality"], method="spearman").sort_values()
    corr = rho.rename_axis("feature").reset_index(name="spearman_rho")
    st.altair_chart(alt.Chart(corr).mark_bar().encode(
        x=alt.X("spearman_rho:Q", title="Spearman correlation with quality"),
        y=alt.Y("feature:N", sort=list(corr["feature"]), title=None),
        color=alt.condition(alt.datum.spearman_rho > 0, alt.value("#5B7F6B"), alt.value(BERRY)),
        tooltip=["feature", alt.Tooltip("spearman_rho:Q", format=".3f")]), width="stretch")


def page_reproduction():
    st.title("Review 1 — reproducing the paper")
    st.write("Stratified 10-fold cross-validation repeated 10 times (100 fold-runs, 15,990 pooled predictions). "
             "The paper's RNN and ELM are replaced by Gradient Boosting and an MLP (classical-ML syllabus); "
             "SVM and Random Forest are unchanged.")
    ranking = r1("model_accuracy_summary.csv").rename(columns={"overall_accuracy_pct": "accuracy (%)"})
    left, right = st.columns([2, 3])
    with left:
        st.subheader("Model ranking")
        st.dataframe(ranking.round(2), hide_index=True, width="stretch")
    with right:
        st.altair_chart(alt.Chart(ranking).mark_bar().encode(
            x=alt.X("accuracy (%):Q", scale=alt.Scale(domain=[55, 75])),
            y=alt.Y("model:N", sort="-x", title=None),
            color=alt.condition(alt.datum.model == "Ensemble (soft vote)", alt.value(BERRY), alt.value(MUTED))),
            width="stretch")

    st.subheader("Per-class comparison with the published benchmarks")
    figure(R1_FIGS / "accuracy_comparison.png", "Cortez et al. (2009), Ma et al. (2024) and our reproduction, per grade")
    st.dataframe(r1("benchmark_comparison.csv").round(2), hide_index=True, width="stretch")

    st.subheader("Why 89.73 % does not reproduce — checks from the paper's own tables")
    a, b = st.columns(2)
    with a:
        st.caption("Table 9 reconciliation")
        st.dataframe(r1("paper_table9_reconciliation.csv"), hide_index=True, width="stretch")
    with b:
        st.caption("Table 8 weights applied to the paper's base accuracies")
        st.dataframe(r1("paper_internal_consistency_check.csv"), hide_index=True, width="stretch")
    st.warning("Table 9 was transcribed by eye from the printed paper. These are figures we could not reconcile, "
               "not a claim that the paper is wrong.")


def page_balancing():
    st.title("Review 2 — class balancing")
    st.write("The reproduction's four learners and weighted vote under four balancing schemes; only the balancing "
             "changes. SMOTE runs inside each training fold, so the test fold is never resampled.")
    a = r2("A_class_balancing.csv")
    ens = a[a["model"] == "Ensemble (paper weights)"][["balancing_label", "accuracy", "balanced_accuracy",
                                                      "macro_f1", "recall_3", "recall_4", "recall_7", "recall_8"]]
    st.dataframe(ens.rename(columns={"balancing_label": "scheme"}).round(2), hide_index=True, width="stretch")
    figure(R2_FIGS / "A_class_balancing.png", "Accuracy, macro-F1 and per-class recall under each scheme")


def page_improvement():
    st.title("Review 2 — improving the result")
    st.subheader("1 · Testing the Review-1 diagnosis: sharpening the weights")
    figure(R2_FIGS / "B1_weight_temperature.png", "Weight temperature T (T = 1 is the paper). Diagnostic only.")
    st.subheader("2 · The fix: temperature learned inside each training fold")
    c1, c2 = st.columns([3, 2])
    with c1:
        figure(R2_FIGS / "B4_chosen_temperatures.png", "Temperature chosen by each fold's inner cross-validation")
    with c2:
        p = r2("paired_comparison.csv")
        st.dataframe(p.assign(model=p["model"].map(short), compared_with=p["compared_with"].map(short))
                     [["model", "compared_with", "metric", "mean_difference", "repeats_won", "wilcoxon_p"]].round(3),
                     hide_index=True, width="stretch")
        st.caption("Paired across the 10 repeats. Repeats reuse the same wines, so p-values are indicative.")
    st.subheader("3 · Every candidate: the accuracy vs. macro-F1 trade-off")
    figure(R2_FIGS / "B_tradeoff.png", "No model wins both metrics; the dashed line is the best-trade-off frontier")
    comp = r2("model_comparison.csv")
    comp["model"] = comp["model"].map(short)
    st.dataframe(comp[["rank_by_macro_f1", "model", "kind", "accuracy", "balanced_accuracy", "macro_f1"]].round(2),
                 hide_index=True, width="stretch", height=420)


def page_importance():
    st.title("Feature importance")
    st.write("Permutation importance on held-out folds (primary), Random Forest impurity importance and Spearman "
             "correlation, checked against each other and against the attributes the paper highlights.")
    figure(R2_FIGS / "C1_permutation_importance.png", "Macro-F1 lost when each measurement is shuffled")
    figure(R2_FIGS / "C2_importance_methods_and_direction.png", "Three importance measures, and direction of effect")
    figure(R2_FIGS / "C3_feature_subset.png", "How many lab tests the model needs")
    st.dataframe(r2("C_feature_importance.csv")[["rank_final", "feature", "final_f1_drop", "rf_f1_drop", "rf_mdi",
                                                 "spearman_rho", "highlighted_by_paper"]].round(3),
                 hide_index=True, width="stretch")


def page_predict():
    st.title("Predict a wine's quality")
    df = load_data()
    models = trained_models()

    examples = {"Typical wine (median of all wines)": df[FEATURE_COLUMNS].median()}
    for g in (4, 5, 6, 7, 8):
        examples[f"Typical grade-{g} wine"] = df[df["quality"] == g][FEATURE_COLUMNS].median()
    start = st.selectbox("Start from", list(examples), help="Fills the sliders with the median measurements of that group.")
    base = examples[start]

    st.write("Adjust the 11 laboratory measurements:")
    values = {}
    cols = st.columns(3)
    for i, f in enumerate(FEATURE_COLUMNS):
        lo, hi = float(df[f].min()), float(df[f].max())
        step = 10 ** np.floor(np.log10((hi - lo) / 200)) if hi > lo else 0.01
        decimals = int(min(5, max(0, -np.floor(np.log10(step)))))
        values[f] = cols[i % 3].slider(f, lo, hi, float(np.clip(base[f], lo, hi)), step=float(step),
                                       format=f"%.{decimals}f", key=f"{start}-{f}")
    x = pd.DataFrame([values])[FEATURE_COLUMNS].to_numpy()

    st.divider()
    out = st.columns(len(models))
    for col, (name, model) in zip(out, models.items()):
        proba = model.predict_proba(x)[0]
        pred = int(model.classes_[proba.argmax()])
        with col:
            st.subheader(name)
            st.caption("Best accuracy (71.03 %)" if name == "Random Forest" else "Best on the rare grades (macro-F1 40.92)")
            st.metric("Predicted quality grade", pred, help=MODELS[name])
            prob = pd.DataFrame({"grade": [str(c) for c in model.classes_], "probability": proba})
            st.altair_chart(alt.Chart(prob).mark_bar().encode(
                x=alt.X("grade:O", title="Quality grade", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("probability:Q", scale=alt.Scale(domain=[0, 1])),
                color=alt.condition(alt.datum.grade == str(pred), alt.value(BERRY), alt.value(MUTED)),
                tooltip=["grade", alt.Tooltip("probability:Q", format=".1%")]), width="stretch")
    st.caption("Models trained on all 1,599 wines with the project's settings. Under cross-validation the "
               "forest is right about 71 % of the time; grades 3, 4 and 8 are rare and hard to predict.")

    st.divider()
    st.subheader("Batch prediction")
    st.write("Upload a CSV with the 11 measurement columns (comma or semicolon separated).")
    sample = df[FEATURE_COLUMNS].sample(10, random_state=42)
    st.download_button("Download a sample input file", sample.to_csv(index=False), "sample_wines.csv", "text/csv")
    up = st.file_uploader("CSV file", type=["csv"])
    if up is not None:
        batch = pd.read_csv(up, sep=None, engine="python")
        missing = [f for f in FEATURE_COLUMNS if f not in batch.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            res = batch.copy()
            for name, model in models.items():
                res[f"predicted · {name.split(' (')[0]}"] = model.predict(batch[FEATURE_COLUMNS].to_numpy())
            st.dataframe(res, width="stretch")
            st.download_button("Download predictions", res.to_csv(index=False), "predictions.csv", "text/csv")


pages = [
    st.Page(page_overview, title="Overview", default=True),
    st.Page(page_dataset, url_path="dataset", title="Dataset"),
    st.Page(page_reproduction, url_path="reproduction", title="Review 1: reproduction"),
    st.Page(page_balancing, url_path="class-balancing", title="Review 2: class balancing"),
    st.Page(page_improvement, url_path="improvement", title="Review 2: improving the result"),
    st.Page(page_importance, url_path="feature-importance", title="Feature importance"),
    st.Page(page_predict, url_path="predict", title="Predict a wine"),
]
# Guarded so the test suite can import the page functions without running the app.
if __name__ == "__main__":
    nav = st.navigation(pages)
    with st.sidebar:
        st.markdown("**Wine Quality Prediction**")
        st.caption("Surianandhan S · 127018060\n\nCSE425 Machine Learning Essentials\n\nSASTRA Deemed to be University")
    nav.run()
