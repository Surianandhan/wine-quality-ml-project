"""
build_paper.py -- the conference paper (Word) in the format of the course's paper template.

    python report/build_paper.py            # writes report/Conference_Paper_127018060.docx
    python report/build_paper.py --render   # also writes a PDF preview (Pages) to report/data/

Same sources as build_report.py: numbers from tools/results.py, references
from tools/refs.py. Built twice in memory so that figure, table, equation and
citation numbers are known before they are written.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))
from docxkit import Doc, X, latex_to_omml, md, ppr, run  # noqa: E402
from refs import REFS, Citations  # noqa: E402
import results as R  # noqa: E402

TEMPLATE = HERE / "templates" / "paper_template.docx"
OUT = HERE / "Conference_Paper_127018060.docx"
FIG = HERE / "figures"
F2 = R.ROOT / "results" / "review2" / "figures"

TITLE = "Reproducing a Weighted Ensemble for Wine Quality Prediction: Flat Weights, Class Balancing and Feature Importance"
AUTHOR = "Surianandhan S"
AFFIL = "SASTRA Deemed to be University, Thanjavur, Tamilnadu, India"
EMAIL = "suria24aus@gmail.com"
GUIDE = "Dr. Vidivelli S"
APP = R.APP_URL or "[app link – added after deployment]"
REPO = R.REPO_URL or "[GitHub link – added after deployment]"

IND = dict(ind_left=284, ind_right=288)
DUMMY_MATH = '<m:oMathPara><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></m:oMathPara>'
f2 = R.f2


def g(name, col):
    return float(R.cm(name)[col])


class Paper:
    def __init__(self, prev=None, cache=None):
        self.d = Doc(TEMPLATE)
        prev = prev or {}
        self.prev_reg = prev.get("reg", {})
        self.cite = Citations(prev.get("cited", set()))
        self.cache = cache or {}
        self.reg, self.cited, self.latex = {}, set(), []
        self.nfig = self.ntab = self.neq = 0

    def T(self, s):
        s = re.sub(r"\[\[([\w.-]+)\]\]", lambda m: self.prev_reg.get(m.group(1), "?"), s)

        def cit(m):
            keys = [k.strip() for k in m.group(1).split(",")]
            for k in keys:
                if k not in REFS:
                    raise KeyError(k)
            self.cited.update(keys)
            return self.cite(*keys)
        return re.sub(r"\{c:([\w, ]+)\}", cit, s)

    # blocks
    def para(self, s):
        self.d.p(md(self.T(s)), ppr(after=60, jc="both", **IND))

    def section(self, title):
        self.d.p(run(title, b=True, caps=True), ppr(keep_next=True, before=240, after=60, jc="both", **IND))

    def sub(self, title):
        self.d.p(run(title, b=True), ppr(keep_next=True, before=120, after=40, jc="both", **IND))

    def subsub(self, title):
        self.d.p(run(title, b=True), ppr(keep_next=True, before=60, jc="both", **IND))

    def numbered(self, items):
        nid = self.d.new_list(11)
        for it in items:
            self.d.p(md(self.T(it)), ppr(num=nid, jc="both"))

    def figure(self, key, path, caption, width=6.0):
        self.nfig += 1
        self.reg[key] = str(self.nfig)
        self.d.picture(path, width, ppr(keep_next=True, after=40, line=240, jc="center"))
        self.d.p(md(f"Fig. {self.nfig}: " + self.T(caption)), ppr(after=120, line=240, jc="center", **IND))

    def table(self, key, caption, header, rows, widths, align=None, bold_rows=()):
        self.ntab += 1
        self.reg[key] = str(self.ntab)
        self.d.p(md(f"Table {self.ntab}: " + self.T(caption), b=True), ppr(keep_next=True, before=120, after=60, line=240, jc="center", **IND))
        self.d.grid_table([self.T(h) for h in header], [[self.T(str(c)) for c in r] for r in rows], widths, sz=19,
                          align=align, bold_rows=bold_rows)
        self.d.p("", ppr(after=80, line=240, jc="both"))

    def eqs(self, items):
        maths, labels = [], []
        for key, latex in items:
            self.neq += 1
            self.reg[key] = str(self.neq)
            self.latex.append(latex)
            el = self.cache.get(latex)
            maths.append(el if el is not None else X(DUMMY_MATH))
            labels.append(str(self.neq))
        self.d.eq_table(maths, labels, widths=(864, 6696, 864))

    def statement(self, label, text, before=None):
        self.d.p(run(label, b=True) + md(" " + self.T(text)), ppr(before=before, after=60, jc="both", **IND))

    def references(self):
        self.d.p(run("References", b=True), ppr(keep_next=True, before=200, after=60, jc="both", **IND))
        nid = self.d.new_list(9)
        for k in self.cite.keys:
            pieces, url = REFS[k]
            xml = "".join(run(t, i=it, sz=20) for t, it in pieces)
            if url:
                xml += run(" ", sz=20) + self.d.link(url, url, sz=20)
            self.d.p(xml, ppr(num=nid, after=60, line=276))

    # content
    def build(self):
        d, a = self.d, R.acc
        d.p(run(TITLE, b=True, sz=28), ppr(after=120, jc="center", **IND))
        d.p(run(AUTHOR, b=True), ppr(jc="center", **IND))
        d.p(run(AFFIL, b=True), ppr(jc="center", **IND))
        d.p(run(f"Corresponding author: {EMAIL}"), ppr(after=200, jc="center", **IND))

        best = R.cm(R.RF_SMOTE)
        ens = R.cm(R.ENS_R1)
        abstract = (
            "Predicting a wine's sensory quality grade from routine laboratory measurements would give retailers an early and objective "
            "estimate for purchasing and pricing. This paper reproduces a recent accuracy- and diversity-weighted ensemble for this task "
            f"on the UCI red Vinho Verde data ({R.N:,} wines, 11 physicochemical inputs, six imbalanced grades), which reports 89.73 % "
            "accuracy. With stratified 10-fold cross-validation repeated 10 times and all preprocessing fitted inside the training folds, "
            f"the reproduced ensemble reaches {f2(a['Ensemble (soft vote)'])} % and Random Forest alone {f2(a['RF'])} %. The paper's own "
            "tables account for the gap: its weights lie within 0.053 of uniform, its base accuracies imply about "
            f"{f2(R.cons['weighted_average_of_base_accuracies_pct'])} %, and its confusion matrix implies a "
            f"{int(R.t9['implied_test_set_size'])}-wine hold-out at {f2(R.t9['implied_overall_accuracy_pct'])} %. Near-uniform weights make "
            "the ensemble average its members instead of exceeding the best one; learning a weight-sharpening temperature inside each "
            f"training fold raises it to {f2(g(R.LT_R1, 'accuracy'))} %. Class balancing with SMOTE raises macro-F1 from "
            f"{f2(ens['macro_f1'])} to {f2(best['macro_f1'])} and grade-4 recall from {f2(ens['recall_4'])} % to {f2(best['recall_4'])} % "
            f"for {f2(ens['accuracy'] - best['accuracy'])} accuracy points. Permutation importance, impurity importance and rank "
            "correlation agree that alcohol, sulphates and volatile acidity drive the prediction, and four tests give most of the "
            "accuracy. The models are deployed in a Streamlit web application.")
        d.p(run("Abstract:", b=True) + md(" " + abstract), ppr(after=120, jc="both", **IND))
        d.p(run("Keywords:", b=True) + run(" 1. Wine Quality, 2. Ensemble Learning, 3. Reproducibility, 4. Class Imbalance, "
                                           "5. SMOTE, 6. Feature Importance"), ppr(after=120, jc="both", **IND))

        # 1
        self.section("1. Introduction")
        self.para("Retailers stock, price and promote wines by their quality, but the quality grade is assigned by tasters, which is slow "
                  "and partly subjective. The physicochemical tests made on every batch are cheap and objective, so predicting the "
                  "tasters' grade from them has long been studied, starting with Cortez et al. {c:cortez2009}, who released the Vinho "
                  "Verde data {c:cortez2009data}.")
        self.para("Ma et al. {c:ma2024} recently proposed an ensemble of an SVM, a recurrent neural network (RNN), an extreme learning "
                  "machine (ELM) and a Random Forest, combined by weights that reward both the accuracy of each learner and how "
                  "differently it errs. They report 89.73 % accuracy on the red-wine data, 9.02 points above their best learner – far "
                  "above the accuracies usually reported for this six-grade task. This paper reproduces the method, explains why the "
                  "published figure is not reached, and extends it. The objectives are:")
        self.numbered([
            "To reproduce the four learners and the weighted ensemble with leakage-free, repeated cross-validation.",
            "To check the published results against the paper's own tables.",
            "To balance the six imbalanced grades with class weights and SMOTE, and to improve the ensemble without using test data.",
            "To identify the laboratory measurements that drive the prediction, and to deploy the models in a web application.",
        ])

        # 2
        self.section("2. Related Work")
        self.para("Cortez et al. {c:cortez2009} predicted the Vinho Verde grades with an SVM, a neural network and multiple regression "
                  "and ranked the inputs by sensitivity analysis. Gupta {c:gupta2018} selected important features with linear regression "
                  "before predicting quality with neural networks and SVMs, Dahal et al. {c:dahal2021} found gradient boosting the most "
                  "accurate of four learners on red wine, and Bhardwaj et al. {c:bhardwaj2022} enlarged a small set of Pinot noir samples "
                  "with synthetic data before comparing classifiers. Ensembles can outperform their members when the members err "
                  "differently {c:dietterich2000}, {c:zhou2012}, but Kuncheva and Whitaker {c:kuncheva2003} found no simple relation "
                  "between measured diversity and ensemble accuracy. For imbalanced classes, He and Garcia {c:he2009} review the main "
                  "remedies, including SMOTE {c:chawla2002}; for importance, impurity-based scores are biased {c:strobl2007} and "
                  "permutation importance on held-out data is preferred {c:breiman2001}, {c:fisher2019}.")

        # 3
        self.section("3. Proposed Methodology")
        self.para("Fig. [[f_framework]] shows the framework. Part A prepares the data and the protocol, Part B reproduces the base paper, "
                  "Part C adds the three extensions, and Part D evaluates every model in the same way and serves the results in a web "
                  "application. The implementation uses scikit-learn {c:pedregosa2011} and imbalanced-learn {c:lemaitre2017}.")
        self.figure("f_framework", FIG / "framework.png", "The framework of the proposed methodology", 6.0)

        self.sub("3.1 Dataset Description and Preprocessing")
        cc = R.class_counts
        self.para(f"The red-wine data {{c:cortez2009data}} contain {R.N:,} wines with 11 measurements (fixed, volatile and citric acidity, "
                  "residual sugar, chlorides, free and total sulphur dioxide, density, pH, sulphates and alcohol) and the median grade of "
                  f"at least three assessors. Only grades 3–8 occur, with {int(cc[3])}, {int(cc[4])}, {int(cc[5])}, {int(cc[6])}, "
                  f"{int(cc[7])} and {int(cc[8])} wines: grades 5 and 6 hold {100 * (cc[5] + cc[6]) / R.N:.1f} %. All wines and grades "
                  "are kept, as in the base paper. Each feature is min–max scaled (1); the scaler is the first step of a pipeline, so in "
                  "every fold it is fitted on the training wines only.")
        self.eqs([("e_mm", r"x_{ij}' = \frac{x_{ij} - \min_{i} x_{ij}}{\max_{i} x_{ij} - \min_{i} x_{ij}}")])
        self.para("Every model is evaluated with stratified 10-fold cross-validation repeated 10 times (seeds 0–9), giving 15,990 "
                  "out-of-fold predictions per model; all models share the same folds, so they can be compared repeat by repeat.")

        self.sub("3.2 Base Learners and the Weighted Ensemble")
        self.para("SVM {c:cortes1995} (RBF kernel, C = 10, Platt-calibrated) and Random Forest {c:breiman2001} (300 trees) are used as "
                  "in the paper; both have balanced class weights. The RNN and the ELM {c:huang2006} are outside the classical scope of "
                  "the course and are replaced by Gradient Boosting {c:friedman2001} (200 stages), which also refines its prediction "
                  "step by step, and a multilayer perceptron {c:rumelhart1986} with layers (64, 32).")
        self.para("For learner m with out-of-fold predictions, the error indicator gives an error vector e<sub>m</sub> and an error rate "
                  "ε<sub>m</sub>. The accuracy weight is the normalised inverse error (2), the diversity weight the normalised sum of "
                  "distances to the other error vectors (3), and the final weight their average (4). The ensemble adds the weighted class "
                  "probabilities (5), the literal reading of the paper's weighted sum; a hard-vote reading is also reported.")
        self.eqs([("e_acc", r"w_{m}^{acc} = \frac{\varepsilon_{m}^{-T}}{\sum_{j=1}^{M} \varepsilon_{j}^{-T}}"),
                  ("e_div", r"w_{m}^{div} = \frac{D_{m}^{\,T}}{\sum_{j=1}^{M} D_{j}^{\,T}}, \qquad D_{m} = \sum_{j \neq m} \left\| e_{m} - e_{j} \right\|_{2}"),
                  ("e_w", r"w_{m} = \frac{1}{2}\left(w_{m}^{acc} + w_{m}^{div}\right)"),
                  ("e_vote", r"\hat{y}(x) = \arg\max_{k} \sum_{m=1}^{M} w_{m}\, p_{m,k}(x)")])
        self.para("The base paper corresponds to T = 1 in (2) and (3). A temperature T > 1 sharpens the weights towards the most accurate "
                  "(or most diverse) learner.")

        self.sub("3.3 Class Balancing and Improvements")
        self.subsub("a) Class Balancing")
        self.para("Four schemes are compared on the same learners: none; the partial weighting used in the reproduction (SVM and RF "
                  "only); balanced weights for all four learners, given to Gradient Boosting and the MLP as per-sample weights (6); and "
                  "SMOTE {c:chawla2002} inside each training fold after scaling (7), so the test fold is never resampled.")
        self.eqs([("e_sw", r"s_{i} = \frac{N}{K\, n_{y_{i}}}"),
                  ("e_smote", r"x_{new} = x_{i} + \lambda\left(x_{nn} - x_{i}\right), \qquad \lambda \sim U(0,1)")])
        self.subsub("b) Learned Temperature, Stacking and Stronger Members")
        self.para("A sweep of T ∈ {1, …, 100} tests whether flat weights explain the results; because its weights come from the scored "
                  "predictions, it is diagnostic only. The learned-temperature ensemble instead chooses T (and whether to sharpen one or "
                  "both terms) by an inner 5-fold cross-validation inside every outer training fold. Stacking {c:wolpert1992} learns a "
                  "logistic-regression combiner, with and without balanced class weights, and ExtraTrees {c:geurts2006} and "
                  "histogram-based gradient boosting {c:ke2017} are tried as stronger members.")
        self.subsub("c) Feature Importance")
        self.para("Permutation importance (8) is the macro-F1 lost on the held-out fold when feature j is shuffled, averaged over R = 20 "
                  "shuffles and the folds; it is compared with the impurity importance (MDI) of the forest and with the Spearman "
                  "correlation of each feature with quality. Random Forest is also retrained on the top-k features chosen inside each "
                  "training fold.")
        self.eqs([("e_perm", r"I_{j} = S\left(f, X_{test}\right) - \frac{1}{R}\sum_{r=1}^{R} S\left(f, X_{test}^{(j,r)}\right)")])

        self.sub("3.4 Model Evaluation")
        self.para("Accuracy (9) is reported for comparison with the paper. Because grades 5 and 6 dominate, the primary metric of the "
                  "extensions is macro-F1 (10), fixed before those experiments, together with balanced accuracy (11) and per-class recall "
                  "R<sub>k</sub> {c:sokolova2009}. The paper's per-class \"precision\" divides by the true-class totals, i.e. it is recall, "
                  "so recall is used when comparing with it.")
        self.eqs([("e_a", r"\text{Accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}\left[\hat{y}_{i} = y_{i}\right]"),
                  ("e_f1", r"\text{Macro-F1} = \frac{1}{K}\sum_{k=1}^{K} \frac{2\,P_{k}\,R_{k}}{P_{k} + R_{k}}"),
                  ("e_ba", r"\text{Balanced accuracy} = \frac{1}{K}\sum_{k=1}^{K} R_{k}")])

        self.sub("3.5 Web Application")
        self.para("A Streamlit {c:streamlit2026} application presents all results and predicts the grade of a new wine from its 11 "
                  "measurements with two models – the most accurate (Random Forest) and the best on the rare grades (Random Forest with "
                  "SMOTE) – showing the probability of every grade (Fig. [[f_app]]); a CSV file can be scored in bulk. It reuses the "
                  "project's own model definitions, and 15 automated checks confirm that its models and numbers match the experiments. "
                  f"It is deployed on Streamlit Community Cloud at {APP}.")
        self.figure("f_app", FIG / "app" / "parts" / "app_predict_1of1.png", "Web application: the grade of a wine predicted by both models", 4.8)

        # 4
        self.section("4. Results and Discussions")
        self.sub("4.1 Reproduction of the Base Paper")
        pa = R.C.MA_2024_BASE_LEARNER_ACCURACY
        self.para(f"Table [[t_acc]] compares the accuracies. The reproduced ensemble reaches {f2(a['Ensemble (soft vote)'])} % and does not "
                  f"beat Random Forest ({f2(a['RF'])} %), although it beats the other three learners. Table [[t_class]] shows that the "
                  "shape of the paper's per-class result reproduces – grades 5 and 6 are predicted well, the extreme grades poorly – but "
                  "grades 3, 4 and 8 are almost never recognised.")
        self.table("t_acc", "Overall accuracy (%): reference paper result vs our reproduction result",
                   ["Model (paper's learner)", "Reference paper result", "Our reproduction result"],
                   [["SVM", f2(pa["SVM"]), f2(a["SVM"])], ["Gradient Boosting (RNN)", f2(pa["RNN"]), f2(a["GradBoost"])],
                    ["MLP (ELM)", f2(pa["ELM"]), f2(a["MLP"])], ["Random Forest", f2(pa["RF"]), f2(a["RF"])],
                    ["Ensemble, soft vote", "89.73", f2(a["Ensemble (soft vote)"])], ["Ensemble, hard vote", "–", f2(a["Ensemble (hard vote)"])]],
                   [3600, 2736, 2736], align=["left", "center", "center"], bold_rows=(4,))
        me = R.metrics["Ensemble"]
        rows = [[str(c), str(int(R.class_counts[c])), f2(R.C.CORTEZ_2009_PER_CLASS_PRECISION[k]), f2(R.C.MA_2024_PER_CLASS_PRECISION[k]),
                 f2(me.loc[c, "sensitivity_recall"])] for k, c in enumerate(R.CLASSES)]
        self.table("t_class", "Per-class recall (%), the paper's \"precision\"",
                   ["Grade", "Wines", "Cortez et al. (2009)", "Reference paper result", "Our ensemble"], rows,
                   [1296, 1296, 2160, 2304, 2016], align=["center"] * 5)

        self.sub("4.2 Why the Published Accuracy Is Not Reached")
        w = R.our_weights
        self.para("Our final weights stay within "
                  f"{max(abs(v - 0.25) for v in w.values()):.3f} of the uniform 0.25, and the paper's own weights within 0.053, so in both "
                  "cases the ensemble is close to a plain average of its members – and an average of one strong and three weaker learners "
                  "lands between them. Two checks computed from the paper's printed numbers (Table [[t_checks]]) could not be reconciled "
                  "with its 89.73 %: its confusion matrix holds only "
                  f"{int(R.t9['implied_test_set_size'])} wines (a hold-out split) with {f2(R.t9['implied_overall_accuracy_pct'])} % "
                  "correct, and its weights applied to its base accuracies give "
                  f"{f2(R.cons['weighted_average_of_base_accuracies_pct'])} %. The matrix was transcribed by eye, so these are reported as "
                  "unreconciled figures, not as errors of the paper.")
        self.table("t_checks", "Checks computed from the base paper's own tables",
                   ["Quantity", "Value"],
                   [["Wines in the paper's ensemble confusion matrix", f"{int(R.t9['implied_test_set_size'])} of {R.N:,} ({f2(R.t9['implied_fraction_of_dataset_pct'])} %)"],
                    ["Accuracy implied by that matrix", f"{f2(R.t9['implied_overall_accuracy_pct'])} % (reported: 89.73 %)"],
                    ["Weighted average of the paper's base accuracies", f"{f2(R.cons['weighted_average_of_base_accuracies_pct'])} %"],
                    ["Paper's ensemble above that average", f"+{f2(R.cons['gap_vs_weighted_average_pct_points'])} points"],
                    ["Our ensemble above that average", f"+{f2(R.cons['our_gap_vs_their_weighted_average_pct_points'])} points"]],
                   [5184, 3888], align=["left", "center"])
        t = R.temp[(R.temp["balancing"] == "partial") & (R.temp["sharpen"] == "accuracy")].set_index("temperature")
        sp, _ = R.share_sharp("partial")
        self.para("The diagnosis was then tested directly. Sharpening the accuracy term lifts the ensemble from "
                  f"{f2(t.loc[1, 'accuracy'])} % at T = 1 to {f2(t.loc[25, 'accuracy'])} % at T = 25, past Random Forest. Chosen honestly "
                  f"by inner cross-validation, the learned temperature gives {f2(g(R.LT_R1, 'accuracy'))} % accuracy and "
                  f"{f2(g(R.LT_R1, 'macro_f1'))} macro-F1, better than the paper's weights in all 10 repeats on both metrics; T ≥ 10 was "
                  f"chosen in {sp:.0f} % of the folds.")

        self.sub("4.3 Class Balancing and the Best Model")
        b = R.balancing[R.balancing["model"] == "Ensemble (paper weights)"]
        rows = [[x.balancing_label, f2(x.accuracy), f2(x.macro_f1), f"{x.recall_3:.1f}", f"{x.recall_4:.1f}", f"{x.recall_7:.1f}",
                 f"{x.recall_8:.1f}"] for x in b.itertuples()]
        rows.append(["**Best model: RF + SMOTE**", f2(best["accuracy"]), f2(best["macro_f1"]), f"{best['recall_3']:.1f}",
                     f"{best['recall_4']:.1f}", f"{best['recall_7']:.1f}", f"{best['recall_8']:.1f}"])
        self.para("Table [[t_bal]] shows that balancing moves recall from grades 5 and 6 to the rare grades. Of all 28 candidates, "
                  f"Random Forest with SMOTE has the best macro-F1 ({f2(best['macro_f1'])}), just ahead of the learned-temperature ensemble "
                  f"with SMOTE members ({f2(g(R.LT_SMOTE, 'macro_f1'))}); it beats the reproduced ensemble on macro-F1 in 10 of 10 repeats "
                  "and loses on accuracy in 9 of 10. Stacking relearns the majority bias unless its combiner is balanced. No candidate is "
                  "best on both metrics (Fig. [[f_trade]]), so the application offers both the most accurate and the most balanced model.")
        self.table("t_bal", "Class balancing applied to the reproduced ensemble, and the best model (%)",
                   ["Scheme", "Accuracy", "Macro-F1", "R₃", "R₄", "R₇", "R₈"], rows,
                   [3168, 1152, 1152, 864, 864, 864, 1008], align=["left"] + ["center"] * 6, bold_rows=(4,))
        self.figure("f_trade", F2 / "B_tradeoff.png", "Accuracy against macro-F1 for all 28 candidates; the dashed line is the trade-off frontier", 5.4)

        self.sub("4.4 Feature Importance")
        im = R.imp.sort_values("rank_final").head(6)
        rows = [[x.feature, f2(x.final_f1_drop), f"{x.rf_mdi:.3f}", f"{x.spearman_rho:+.2f}"] for x in im.itertuples()]
        s4 = R.subset[R.subset["n_features"] == 4].iloc[0]
        self.para("The three importance measures agree (pairwise rank correlation "
                  f"{R.agree.min():.2f}–{R.agree.max():.2f}): alcohol, sulphates and volatile acidity lead, followed by chlorides and total "
                  "sulphur dioxide (Table [[t_imp]], Fig. [[f_perm]]). Three of the paper's four key attributes are in the top three; "
                  "citric acid ranks sixth. Higher alcohol and sulphates go with better wine, higher volatile acidity with worse. Retrained "
                  f"on four tests chosen inside each fold, Random Forest keeps {f2(s4['accuracy'])} % accuracy, within "
                  f"{f2(a['RF'] - s4['accuracy'])} points of all eleven.")
        self.table("t_imp", "The six most important features of the best model",
                   ["Feature", "Permutation importance (macro-F1 points)", "MDI (Random Forest)", "Spearman ρ with quality"], rows,
                   [2592, 2592, 1872, 2016], align=["left", "center", "center", "center"])
        self.figure("f_perm", F2 / "C1_permutation_importance.png", "Permutation importance on the held-out folds", 5.6)

        # 5
        self.section("5. Conclusions and Future Work")
        self.para("This study reproduced the accuracy- and diversity-weighted ensemble of Ma et al. for wine quality prediction with "
                  f"leakage-free, repeated cross-validation. The ensemble reaches {f2(a['Ensemble (soft vote)'])} % against the published "
                  "89.73 %, and the gap is consistent with the paper's own tables. The cause on our side is structural: normalising inverse "
                  "errors and error distances of similar learners yields near-uniform weights, so the ensemble averages its members; learning "
                  "the weight temperature inside the training folds corrects this. Class balancing with SMOTE gave the best macro-F1 "
                  f"({f2(best['macro_f1'])}) at a stated cost in accuracy, and three importance measures agreed on alcohol, sulphates and "
                  "volatile acidity.")
        self.para("Future work will extend the study to white wine, treat the grade as an ordinal target, select models with nested "
                  "cross-validation and corrected resampled tests {c:nadeau2003}, and add explanations of individual predictions to the "
                  "web application.")

        self.statement("Data Availability Statement:", "The dataset is publicly available from the UCI Machine Learning Repository "
                       f"(https://doi.org/10.24432/C56S3T). The code and web application are available at {REPO}.", before=120)
        self.statement("Funding:", "This research received no external funding.")
        self.statement("Institutional Review Board Statement:", "Not applicable; the study uses a public dataset of laboratory measurements.")
        self.statement("Acknowledgments:", f"The author thanks {GUIDE}, School of Computing, SASTRA Deemed to be University, for guidance "
                       "throughout this work.")
        self.statement("Conflicts of Interest:", "The author declares no conflict of interest.")
        self.references()
        return self


def main():
    first = Paper().build()
    latex = list(dict.fromkeys(first.latex))
    disp, _ = latex_to_omml(latex, [])
    cache = dict(zip(latex, disp))
    paper = Paper({"reg": first.reg, "cited": first.cited}, cache).build()
    paper.d.save(OUT, title=TITLE, author=AUTHOR, subject="Conference paper",
                 keywords="wine quality, ensemble learning, reproducibility, class imbalance, SMOTE, feature importance")
    print("wrote", OUT)
    if "--render" in sys.argv:
        pdf = HERE / "data" / "paper_render.pdf"
        subprocess.run(["osascript", str(HERE / "tools" / "docx2pdf.applescript"), str(OUT), str(pdf)], check=True)
        n = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1)
        print("rendered", n, "pages")


if __name__ == "__main__":
    main()
