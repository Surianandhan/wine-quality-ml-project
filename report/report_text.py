"""
report_text.py -- the content of the project report, chapter by chapter.

Called by build_report.py. Numbers come from tools/results.py (the result CSVs);
[[key]] is replaced by the number of a figure, table, equation or section, and
{c:key} by the citation number of a reference in tools/refs.py.
"""
import re
from pathlib import Path

import results as R
from docxkit import md, pageref, ppr, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIG = HERE / "figures"
F2 = ROOT / "results" / "review2" / "figures"
LOGO = HERE / "assets" / "sastra_logo.png"

STUDENT = "Surianandhan S"
REG = "127018060"
PROGRAMME = "B. Tech Computer Science and Business Systems"
TITLE = "Wine Quality Prediction Using a Weighted Ensemble: Reproduction, Class Balancing and Feature Importance"
MONTH = "October 2026"
YEAR = "2026-27"
GUIDE = "Dr. Vidivelli S"
GUIDE_ROLE = "Assistant Professor–II, School of Computing"

f2, pct = R.f2, R.pct
APP = R.APP_URL or "[app link – added after deployment]"
REPO = R.REPO_URL or "[GitHub link – added after deployment]"


def g(name, col):
    return float(R.cm(name)[col])


# ======================================================================
# Front matter
# ======================================================================
def front_matter(r):
    d = r.d
    # -- title page --
    d.picture(LOGO, 4.9, ppr(keep_next=True, after=40, line=240, jc="center"))
    d.p(run("SCHOOL OF COMPUTING", b=True, sz=28), ppr(before=280, after=40, line=240, jc="center"))
    d.p(run("THANJAVUR, TAMIL NADU, INDIA – 613401", b=True), ppr(after=0, line=240, jc="center"))
    d.p(run(TITLE, b=True, sz=32), ppr(before=1200, after=0, jc="center"))
    d.p(run("Report submitted to the SASTRA Deemed to be University", i=True, sz=28),
        ppr(before=1200, after=0, line=240, jc="center"))
    d.p(run("as a requirement for the course", i=True, sz=28), ppr(after=0, line=240, jc="center"))
    d.p(run("CSE425 – MACHINE LEARNING ESSENTIALS", b=True, sz=28), ppr(before=800, after=0, line=240, jc="center"))
    d.p(run("Submitted by", i=True, sz=28), ppr(before=1000, after=0, line=240, jc="center"))
    d.p(run(STUDENT, b=True, sz=28), ppr(before=280, after=40, line=240, jc="center"))
    d.p(run(f"(Reg. No.: {REG}, {PROGRAMME})", b=True, sz=26), ppr(after=0, line=240, jc="center"))
    d.p(run(MONTH, b=True, sz=28), ppr(before=800, after=0, line=240, jc="center"))
    d.section_break(r.sect_title)

    # -- bonafide certificate --
    d.picture(LOGO, 4.2, ppr(keep_next=True, after=40, line=240, jc="center"))
    d.p(run("SCHOOL OF COMPUTING", b=True, sz=28), ppr(before=200, after=40, line=240, jc="center"))
    d.p(run("THANJAVUR, TAMIL NADU, INDIA – 613401", b=True), ppr(after=0, line=240, jc="center"))
    d.p(d.bookmark("fm_bonafide", run("Bonafide Certificate", b=True, sz=26, u=True)),
        ppr(before=720, after=360, line=240, jc="center"))
    r.search["fm_bonafide"] = ("line", "Bonafide Certificate")
    d.p(run("This is to certify that the report titled ") + run(f"“{TITLE}”", b=True)
        + run(" submitted as a requirement for the course, ") + run("CSE425: Machine Learning Essentials", b=True)
        + run(" for B.Tech. is a bonafide record of the work done by ") + run(STUDENT, b=True)
        + run(f" (Reg. No.: {REG}, B.Tech Computer Science and Business Systems) during the academic year {YEAR}, "
              "in the School of Computing, under my supervision."),
        ppr(after=720, line=360, jc="both"))
    sig = ppr(tabs=[("left", 3888)], after=440, line=240, ind_left=3888, hanging=3888)
    d.p(run("Signature of Project Supervisor", b=True) + run("\t:  "), sig)
    d.p(run("Name with Affiliation", b=True) + run("\t") + run(f":  {GUIDE}, {GUIDE_ROLE}"), sig)
    d.p(run("Date", b=True) + run("\t:  "), sig)
    d.p(run("Project ") + run("Viva voce", i=True) + run(" held on ____________________"), ppr(before=480, after=1200, line=240))
    d.p(run("Examiner 1", b=True) + run("\t") + run("Examiner 2", b=True), ppr(tabs=[("right", 9749)], line=240))
    d.page_break()

    # -- acknowledgements --
    r.front_heading("Acknowledgements", "fm_ack")
    ack = ppr(after=200, line=360, jc="both")
    d.p(run("I would like to thank our Honourable Chancellor ") + run("Prof. R. Sethuraman", b=True)
        + run(" for providing me with an opportunity and the necessary infrastructure for carrying out this project as a part of my curriculum."), ack)
    d.p(run("I would like to thank our Honourable Vice-Chancellor ") + run("Dr. S. Vaidhyasubramaniam", b=True) + run(" and ")
        + run("Dr. S. Swaminathan", b=True) + run(", Dean, Planning & Development, for the encouragement and strategic support at every step of my college life."), ack)
    d.p(run("I extend my sincere thanks to ") + run("Dr. R. Chandramouli", b=True)
        + run(", Registrar, SASTRA Deemed to be University for providing the opportunity to pursue this project."), ack)
    d.p(run("I extend my heartfelt thanks to ") + run("Dr. V. S. Shankar Sriram", b=True) + run(", Dean, School of Computing, ")
        + run("Dr. R. Muthaiah", b=True) + run(", Associate Dean, Research, ") + run("Dr. K. Ramkumar", b=True)
        + run(", Associate Dean, Academics, ") + run("Dr. D. Manivannan", b=True) + run(", Associate Dean, Infrastructure, ")
        + run("Dr. R. Alageswaran", b=True) + run(", Associate Dean, Students Welfare."), ack)
    d.p(run("My guide ") + run(GUIDE, b=True)
        + run(f", {GUIDE_ROLE} was the driving force behind this work from the start. Her comments at the first review – "
              "to complete the class balancing, to improve the result and to study feature importance – shaped the second half "
              "of the project, and her suggestions helped me throughout. I also thank the project review panel members for their "
              "valuable comments, which made this project better."), ack)
    d.p(run("I would like to extend my gratitude to all the teaching and non-teaching faculties of the School of Computing who have "
            "either directly or indirectly helped me in the completion of the project."), ack)
    d.p(run("I gratefully acknowledge all the contributions and encouragement from my family and friends resulting in the successful "
            "completion of this project. I thank you all for providing me an opportunity to showcase my skills through this project."), ack)
    d.page_break()

    # -- lists of figures and tables --
    r.front_heading("List of Figures", "fm_lof")
    r.list_table("fig", r.prev_figs)
    d.page_break()
    r.front_heading("List of Tables", "fm_lot")
    r.list_table("tab", r.prev_tabs)
    d.page_break()

    # -- abbreviations --
    r.front_heading("Abbreviations", "fm_abbr")
    abbr = [
        ("BA", "Balanced Accuracy (mean of the per-class recalls)"),
        ("CV", "Cross-Validation"),
        ("ELM", "Extreme Learning Machine"),
        ("F1", "Harmonic mean of precision and recall"),
        ("FN, FP", "False Negatives, False Positives"),
        ("GB", "Gradient Boosting"),
        ("HistGB", "Histogram-based Gradient Boosting"),
        ("LR", "Logistic Regression"),
        ("MDI", "Mean Decrease in Impurity"),
        ("MLP", "Multilayer Perceptron"),
        ("OOF", "Out-of-Fold (prediction made by a model that did not see the sample)"),
        ("RBF", "Radial Basis Function"),
        ("ReLU", "Rectified Linear Unit"),
        ("RF", "Random Forest"),
        ("RNN", "Recurrent Neural Network"),
        ("SMOTE", "Synthetic Minority Over-sampling Technique"),
        ("SO₂", "Sulphur dioxide"),
        ("SVM", "Support Vector Machine"),
        ("TN, TP", "True Negatives, True Positives"),
        ("UCI", "University of California, Irvine (Machine Learning Repository)"),
    ]
    d.grid_table(["Abbreviation", "Meaning"], abbr, [2304, 6336], sz=22, align=["center", "left"], keep_next=False)
    d.page_break()

    # -- notations --
    r.front_heading("Notations", "fm_not")
    d.p(run("English Symbols", b=True, sz=26))
    english = [
        (r"N", "Number of wines (1,599)"),
        (r"K", "Number of quality classes (6: grades 3 to 8)"),
        (r"M", "Number of base learners in an ensemble"),
        (r"x_{i},\ x_{i}'", "Feature vector of wine i; its min–max scaled value"),
        (r"y_{i},\ \hat{y}_{i}", "True and predicted quality grade of wine i"),
        (r"p_{m}(x)", "Class-probability vector given by learner m for wine x"),
        (r"w_{m}", "Final ensemble weight of learner m"),
        (r"w_{m}^{acc},\ w_{m}^{div}", "Accuracy-based and diversity-based weight of learner m"),
        (r"e_{m}", "0/1 error vector of learner m over all wines"),
        (r"D_{m}", "Diversity of learner m (sum of distances to the other error vectors)"),
        (r"T", "Temperature that sharpens the weights (T = 1 is the paper)"),
        (r"n_{k}", "Number of wines in class k"),
        (r"TP_{k},FP_{k},FN_{k}", "True positives, false positives and false negatives of class k"),
        (r"P_{k},R_{k},F1_{k}", "Precision, recall and F1 score of class k"),
        (r"I_{j}", "Permutation importance of feature j"),
        (r"B", "Number of trees in a Random Forest"),
    ]
    greek = [
        (r"\varepsilon_{m}", "Cross-validated error rate of learner m"),
        (r"\lambda", "Random interpolation factor of SMOTE, drawn from U(0, 1)"),
        (r"\gamma", "Width parameter of the RBF kernel"),
        (r"\eta", "Learning rate of Gradient Boosting"),
        (r"\alpha_{i}", "Dual coefficients of the SVM"),
        (r"\rho", "Spearman rank correlation"),
    ]
    note = ppr(tabs=[("left", 2016)], after=60)
    for latex, text in english:
        el = d.p(run("\t" + text), note)
        el.insert(1, r.inline_math(latex))
    d.p(run("Greek Symbols", b=True, sz=26), ppr(before=240))
    for latex, text in greek:
        el = d.p(run("\t" + text), note)
        el.insert(1, r.inline_math(latex))
    d.page_break()

    # -- general terms --
    r.front_heading("General Terms", "fm_terms")
    terms = [
        ("Classification", "Assigning each sample to one of a fixed set of classes; here, a wine to one of six quality grades."),
        ("Ensemble Learning", "Combining several models so that their joint prediction is more reliable than that of any one of them."),
        ("Weighted Voting", "Combining the members of an ensemble with a weight per member: a soft vote adds their class probabilities, a hard vote adds their predicted labels."),
        ("Diversity", "The degree to which the members of an ensemble make different errors; an ensemble only helps when its members disagree."),
        ("Class Imbalance", "A large difference in the number of samples per class; here grades 5 and 6 hold 82.5 % of the wines and grades 3 and 8 only 1.75 %."),
        ("Class Weighting", "Giving the samples of rare classes a larger weight in training, so that errors on them cost more."),
        ("SMOTE", "Creating synthetic training samples of a rare class by interpolating between a sample and one of its nearest neighbours of the same class."),
        ("Stratified Cross-Validation", "Splitting the data into k folds with the same class proportions, training on k – 1 folds and testing on the remaining one, k times."),
        ("Data Leakage", "Letting information from the test data reach the training step (for example, through a scaler fitted on all the data), which gives optimistic scores."),
        ("Macro-F1", "The F1 score averaged over the classes with equal weight, so that a rare class counts as much as a common one."),
        ("Balanced Accuracy", "The average of the per-class recalls; a model that always predicts the majority class scores only 1/K."),
        ("Stacking", "Training a second-level model (here a logistic regression) to combine the predictions of the ensemble members."),
        ("Permutation Importance", "The drop in a model's score on held-out data when the values of one feature are shuffled."),
        ("Reproduction Study", "Re-implementing a published method on the same data to check whether its results can be obtained independently."),
        ("Web Application", "An interactive Streamlit front end that presents the results and predicts the quality of new wines in a browser."),
    ]
    for t, s in terms:
        d.p(run(t + ":", b=True) + md(" " + s), ppr(after=160, jc="both"))
    d.page_break()

    # -- abstract --
    r.front_heading("Abstract", "fm_abstract")
    ab = ppr(after=200, line=360, jc="both")
    rf_acc, ens_acc = R.acc["RF"], R.acc["Ensemble (soft vote)"]
    best = R.cm(R.RF_SMOTE)
    abstract = [
        "Wine retailers price, stock and promote wines by their quality grade, but the grade comes from a panel of tasters, "
        "while the physicochemical laboratory measurements of every batch are cheap, objective and available early. This project "
        f"reproduces the weighted-ensemble framework of Ma et al. (Journal of Business Research, 2024), which predicts the tasters' grade "
        f"of the {R.N:,} red Vinho Verde wines of the UCI Wine Quality dataset from 11 laboratory measurements and reports an "
        "overall accuracy of 89.73 %, and then extends it as requested at the first review.",
        "The four base learners of the paper are SVM, a recurrent neural network, an extreme learning machine and Random Forest; "
        "under the classical machine-learning scope of the course the two neural models are replaced by Gradient Boosting and a "
        "multilayer perceptron. Each learner is weighted by the average of an accuracy weight (normalised inverse cross-validated "
        "error) and a diversity weight (normalised distances between error vectors), and the weighted probabilities are summed. "
        "All models are evaluated with stratified 10-fold cross-validation repeated 10 times, with min–max scaling fitted inside "
        f"each training fold. The reproduced ensemble reaches {f2(ens_acc)} % accuracy and Random Forest alone {f2(rf_acc)} %. "
        "Checks computed from the paper's own tables explain the gap: its final weights are close to uniform, its base accuracies "
        f"imply about {f2(R.cons['weighted_average_of_base_accuracies_pct'])} %, and its confusion matrix implies a "
        f"{int(R.t9['implied_test_set_size'])}-wine hold-out with {f2(R.t9['implied_overall_accuracy_pct'])} % accuracy.",
        "Three extensions follow. Class balancing (class weights on all learners, and SMOTE inside each training fold) raises the "
        f"rare-class recall: the best model, Random Forest with SMOTE, raises macro-F1 from {f2(g(R.ENS_R1, 'macro_f1'))} to "
        f"{f2(best['macro_f1'])} and class-4 recall from {f2(g(R.ENS_R1, 'recall_4'))} % to {f2(best['recall_4'])} %, at a cost of "
        f"{f2(g(R.ENS_R1, 'accuracy') - best['accuracy'])} accuracy points. Learning the sharpness of the ensemble weights inside each "
        f"training fold improves the paper's own ensemble to {f2(g(R.LT_R1, 'accuracy'))} %. Permutation importance, impurity "
        "importance and rank correlation agree that alcohol, sulphates and volatile acidity drive the prediction, and four "
        "laboratory tests already give most of the accuracy. The models are delivered through a deployed Streamlit web application.",
    ]
    for s in abstract:
        d.p(md(s), ab)
    d.p(run("Keywords:", b=True) + run(" Wine Quality, Ensemble Learning, Weighted Voting, Reproduction Study, Class Imbalance, "
                                       "SMOTE, Random Forest, Permutation Importance, Streamlit"), ab)
    d.page_break()

    # -- table of contents --
    r.front_heading("Table of Contents", "fm_toc")
    rows = []
    for name, bm in [("Bonafide Certificate", "fm_bonafide"), ("Acknowledgements", "fm_ack"), ("List of Figures", "fm_lof"),
                     ("List of Tables", "fm_lot"), ("Abbreviations", "fm_abbr"), ("Notations", "fm_not"),
                     ("General Terms", "fm_terms"), ("Abstract", "fm_abstract")]:
        rows.append(["", run(name, sz=22), pageref(bm, r.page(bm), sz=22)])
    for kind, num, title, bm in r.prev_toc:
        if kind == "chapter":
            rows.append([run(num, b=True, sz=22), run(title, b=True, sz=22), pageref(bm, r.page(bm), b=True, sz=22)])
        else:
            rows.append([run(num, sz=22), run(title, sz=22), pageref(bm, r.page(bm), sz=22)])
    d.grid_table(["Section", "Title", "Page No."], rows, [1440, 6768, 1296], sz=22,
                 align=["center", "left", "center"], keep_next=False)
    d.section_break(r.sect_front)


# ======================================================================
# Chapters
# ======================================================================
def chapters(r):
    chapter1(r)
    chapter2(r)
    chapter3(r)
    chapter4(r)
    chapter5(r)
    chapter6(r)
    chapter7(r)
    chapter8(r)


def chapter1(r):
    r.chapter("SUMMARY OF THE BASE PAPER")
    r.meta("Paper Title:", "From vineyard to table: Uncovering wine quality for sales management through machine learning")
    r.meta("Authors:", "Rui Ma, Di Mao, Dongmei Cao, Shuai Luo, Suraksha Gupta and Yichuan Wang (University of Greenwich, "
           "Nottingham Trent University, State Grid Tianjin Electric Power Company, Newcastle University and University of Sheffield)")
    r.meta("Journal Name:", "Journal of Business Research")
    r.meta("Publisher:", "Elsevier")
    r.meta("Year of Publication:", "2024")
    r.meta("Volume and Article:", "Volume 176, Article 114576 (15 pages)")
    r.meta("DOI:", "https://doi.org/10.1016/j.jbusres.2024.114576")
    r.meta("Indexing Status:", "The Journal of Business Research is a peer-reviewed Elsevier journal indexed in Scopus and in the "
           "Social Sciences Citation Index (Clarivate Web of Science).")

    r.h2("Introduction")
    r.para("A wine retailer decides which wines to buy, how to price them and how to present them largely by their quality, but the "
           "quality grade is assigned by a panel of trained tasters. Sensory assessment is slow, costly and partly subjective. The "
           "physicochemical tests made on every batch – acidity, residual sugar, sulphur dioxide, density, alcohol and so on – are "
           "cheap, objective and available before the wine reaches the shelf. If the tasters' grade can be predicted from these "
           "tests, a retailer gains an early and consistent estimate of quality that can support purchasing, pricing and promotion.")
    r.para("The base paper {c:ma2024} builds such a predictor for the 1,599 red Vinho Verde wines of the UCI Wine Quality dataset "
           "{c:cortez2009data}. It trains four different learners – a support vector machine (SVM), a recurrent neural network (RNN), "
           "an extreme learning machine (ELM) and a Random Forest (RF) – and combines them in a weighted vote in which each learner's "
           "weight rewards both its accuracy and how differently it errs from the others. The paper reports an overall accuracy of "
           "**89.73 %**, 9.02 points above its best single learner, and identifies alcohol, sulphates, volatile acidity and citric "
           "acid as the attributes that matter most.")
    r.para("This project reproduces that framework within the classical machine-learning scope of the course, extends it in "
           "response to the comments of the first review – class balancing, an improved result and feature importance – and delivers "
           "the models through a web application. Throughout the report, values published in the paper are labelled **Reference "
           "Paper Result** and values obtained here **Our Reproduction Result**, so that the two are never mixed.")

    r.h2("Related Works")
    r.para("Cortez et al. {c:cortez2009} collected the Vinho Verde data used here {c:cortez2009data} and modelled the quality grade "
           "from the physicochemical tests with an SVM, a neural network and multiple regression, finding the SVM the most accurate "
           "and using a sensitivity analysis to rank the inputs. Later studies used the same or similar data with other learners: "
           "Gupta {c:gupta2018} first selected the important features with linear regression and then predicted quality with neural "
           "networks and SVMs; Dahal et al. {c:dahal2021} compared ridge regression, an SVM, gradient boosting and a neural network on "
           "red wine and found gradient boosting the most accurate; and Bhardwaj et al. {c:bhardwaj2022} predicted the quality of New "
           "Zealand Pinot noir wines from chemical measurements, enlarging a very small sample with synthetic data before comparing "
           "several classifiers.")
    r.para("The base paper's idea of combining learners rests on the ensemble literature. Dietterich {c:dietterich2000} explains why "
           "an ensemble can outperform its members, and Zhou {c:zhou2012} surveys combination rules including weighted voting and "
           "stacking {c:wolpert1992}. Kuncheva and Whitaker {c:kuncheva2003} compared many measures of diversity between classifiers "
           "and found no simple link between diversity and ensemble accuracy – a point that becomes important in Chapter 4. The learners "
           "come from Cortes and Vapnik {c:cortes1995} (SVM), Breiman {c:breiman2001} (Random Forest), Friedman {c:friedman2001} "
           "(Gradient Boosting), Rumelhart et al. {c:rumelhart1986} (back-propagation networks) and Huang et al. {c:huang2006} (ELM). "
           "For the second review, He and Garcia {c:he2009} review learning from imbalanced data, Chawla et al. {c:chawla2002} "
           "introduced SMOTE, Strobl et al. {c:strobl2007} showed that impurity-based importance is biased, and Fisher et al. "
           "{c:fisher2019} give the theory behind permutation importance. Table [[t_related]] summarises the studies closest to "
           "this project.")
    r.table("t_related", "Summary of related works",
            ["Author and year", "Contribution / finding", "Methods"],
            [["Ma et al. (2024) {c:ma2024} – base paper", "Weighted ensemble for red-wine quality; reports 89.73 % accuracy, 9.02 points above its best learner", "SVM, RNN, ELM, RF; accuracy- and diversity-weighted vote"],
             ["Cortez et al. (2009) {c:cortez2009}", "Introduced the Vinho Verde data; predicted quality from 11 laboratory tests and ranked the inputs", "SVM, neural network, multiple regression"],
             ["Gupta (2018) {c:gupta2018}", "Selected the important physicochemical features before predicting quality", "Linear regression (selection); neural network, SVM"],
             ["Dahal et al. (2021) {c:dahal2021}", "Compared four learners for red-wine quality; gradient boosting was the most accurate", "Ridge regression, SVM, gradient boosting, neural network"],
             ["Bhardwaj et al. (2022) {c:bhardwaj2022}", "Predicted Pinot noir quality from chemical data, enlarging a small sample with synthetic data", "Several classifiers; synthetic oversampling"],
             ["Kuncheva and Whitaker (2003) {c:kuncheva2003}", "Studied diversity measures for classifier ensembles; no simple link between diversity and accuracy", "Pairwise and non-pairwise diversity measures"],
             ["Chawla et al. (2002) {c:chawla2002}", "Oversampled minority classes with synthetic samples interpolated between neighbours", "SMOTE"]],
            [2448, 4464, 2736])

    r.h2("Problem Statement")
    r.para("Given the 11 physicochemical measurements of a red wine, the problem is to predict the quality grade assigned by the "
           "tasters. The grades are heavily imbalanced – grades 5 and 6 hold 82.5 % of the wines and grades 3 and 8 only 1.75 % – so a "
           "model can reach a high accuracy while never recognising the very poor or the excellent wines, which are exactly the ones a "
           "retailer most needs to find. The project must therefore (i) check whether the weighted ensemble of the base paper really "
           "reaches the reported accuracy when it is evaluated without information leaking from the test folds, (ii) improve the "
           "prediction of the rare grades, and (iii) explain which measurements drive the prediction.")

    r.h2("Objectives")
    r.numbered([
        "To reproduce the four base learners and the accuracy- and diversity-weighted ensemble of the base paper on the UCI red-wine data.",
        "To evaluate every model with stratified 10-fold cross-validation repeated 10 times, with all preprocessing fitted inside the training folds.",
        "To compare the reproduction with the published results and to check the paper's figures against its own tables.",
        "To balance the classes with class weights and with SMOTE, and to measure the effect on every class.",
        "To improve the result by sharpening the ensemble weights, by stacking and by stronger members, without using the test folds for any choice.",
        "To measure feature importance with three methods and to find how many laboratory tests are needed.",
        "To deliver the models through a tested, deployed web application.",
    ])

    r.h2("Methodology and Results of the Base Paper")
    r.para("The paper min–max normalises the 11 attributes and trains four base learners – SVM, RNN, ELM and RF – each evaluated by "
           "10-fold cross-validation repeated over 100 experiments. Each learner then receives two weights. The accuracy weight is its "
           "inverse cross-validated error, normalised over the learners. The diversity weight is the sum of the Euclidean distances "
           "between its 0/1 error vector and those of the other learners, also normalised. The final weight is the average of the two, "
           "and the ensemble prediction is the weighted sum of the learners' outputs. The paper reports per-class results for the six "
           "grades present (3 to 8), compares them with Cortez et al. {c:cortez2009}, and studies how the attributes relate to quality. "
           "Tables [[t_paper_acc]] and [[t_paper_class]] list the published values this project compares against.")
    r.para("The main contributions of the paper are:")
    r.numbered([
        "a framework that turns product attributes into a quality prediction a retailer can act on;",
        "an ensemble that weights heterogeneous learners by both accuracy and diversity, reported to beat each learner and earlier studies; and",
        "an analysis of the attributes – alcohol, sulphates, volatile acidity and citric acid – most associated with higher quality.",
    ])
    paper_w = R.C.MA_2024_TABLE8_WEIGHT_SUM
    paper_a = R.C.MA_2024_BASE_LEARNER_ACCURACY
    r.table("t_paper_acc", "Reference Paper Result: accuracy and final weight of each learner",
            ["Learner", "Overall accuracy (%)", "Final weight wᵢ (paper's Table 8)"],
            [["SVM", f2(paper_a["SVM"]), f"{paper_w['SVM']:.4f}"], ["RNN", f2(paper_a["RNN"]), f"{paper_w['RNN']:.4f}"],
             ["ELM", f2(paper_a["ELM"]), f"{paper_w['ELM']:.4f}"], ["Random Forest", f2(paper_a["RF"]), f"{paper_w['RF']:.4f}"],
             ["**Weighted ensemble**", "**89.73**", "–"]],
            [3600, 2700, 3200], align=["left", "center", "center"])
    rows = []
    for k, c in enumerate(R.CLASSES):
        rows.append([str(c), str(int(R.class_counts[c])), f2(R.C.CORTEZ_2009_PER_CLASS_PRECISION[k]), f2(R.C.MA_2024_PER_CLASS_PRECISION[k])])
    rows.append(["Overall", f"{R.N:,}", "–", "89.73"])
    r.table("t_paper_class", "Reference Paper Result: per-class results of the ensemble (%), with the earlier benchmark",
            ["Quality grade", "Wines", "Cortez et al. (2009)", "Ma et al. (2024)"], rows,
            [2000, 2000, 2800, 2800], align=["center"] * 4, bold_rows=(6,))

    r.h2("Scope of this Project")
    r.bullets([
        f"**Dataset:** the red-wine part of the UCI Wine Quality data ({R.N:,} wines), as in the paper; all six grades are kept.",
        "**Learners:** SVM and Random Forest as in the paper; Gradient Boosting replaces the RNN and a multilayer perceptron replaces "
        "the ELM, because recurrent networks and extreme learning machines are outside the classical machine-learning scope of the course.",
        "**Evaluation:** stratified 10-fold cross-validation × 10 repeats (100 fold-runs), with scaling inside each training fold.",
        "**Review 2:** class balancing, improvement of the result and feature importance, each evaluated with the same protocol.",
        f"**Deployment:** a Streamlit web application, published at {APP}.",
    ])


def chapter2(r):
    r.chapter("PROPOSED ARCHITECTURE AND DATA PREPROCESSING")
    r.h2("Proposed Architecture")
    r.para("Figure [[f_framework]] shows the complete workflow. Part A prepares the data and fixes the evaluation protocol. Part B "
           "reproduces the base paper: four base learners, the accuracy and diversity weights, the weighted vote and checks of the "
           "paper's own figures (Review 1). Part C makes the three changes requested at the first review: class balancing, a better "
           "result and feature importance (Review 2). Part D evaluates every model in the same way and delivers the results through the "
           "report and a web application. Every step that involves randomness uses a fixed seed, so all results are reproducible.")
    r.figure("f_framework", FIG / "framework.png", "Proposed architecture of the project", 6.6)

    r.h2("Dataset Description")
    r.para("The dataset is the red-wine part of the Wine Quality data of the UCI Machine Learning Repository {c:cortez2009data}, "
           "collected by Cortez et al. {c:cortez2009}. Each row is one wine with 11 physicochemical measurements and the quality "
           "grade given by sensory assessors (Table [[t_dataset]]).")
    r.table("t_dataset", "Description of the red-wine dataset",
            ["Attribute", "Value"],
            [["Source", "UCI Machine Learning Repository {c:cortez2009data}"],
             ["Wines", "Red Vinho Verde wines from the north-west of Portugal"],
             ["Size", f"{R.N:,} rows × 12 columns (11 inputs and the quality grade)"],
             ["Inputs", "fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free and total sulphur dioxide, density, pH, sulphates, alcohol"],
             ["Target", "quality on a 0–10 scale, the median of at least three sensory assessments; only grades 3–8 occur"],
             ["Missing values", "none"],
             ["Duplicates", f"{R.n_duplicates} rows repeat an earlier row exactly; all rows are kept, as in the base paper"]],
            [2016, 7344])
    units = {"fixed acidity": "g(tartaric acid)/dm³", "volatile acidity": "g(acetic acid)/dm³", "citric acid": "g/dm³",
             "residual sugar": "g/dm³", "chlorides": "g(sodium chloride)/dm³", "free sulfur dioxide": "mg/dm³",
             "total sulfur dioxide": "mg/dm³", "density": "g/cm³", "pH": "–", "sulphates": "g(potassium sulphate)/dm³",
             "alcohol": "% vol."}
    rows = []
    for f in R.FEATURES:
        s = R.desc.loc[f]
        dec = 4 if f in ("density",) else (3 if s["max"] < 2 else 2)
        rows.append([f, units[f], f"{s['min']:.{dec}f}", f"{s['max']:.{dec}f}", f"{s['mean']:.{dec}f}", f"{s['std']:.{dec}f}",
                     f"{R.pearson[f]:+.3f}"])
    r.para("Table [[t_stats]] summarises the 11 measurements. Their ranges differ by four orders of magnitude – density varies in the "
           "third decimal place, total sulphur dioxide up to 289 mg/dm³ – which is why the features are scaled before training.")
    r.table("t_stats", f"Descriptive statistics of the 11 measurements ({R.N:,} wines) and their Pearson correlation r with quality",
            ["Feature", "Unit", "Min", "Max", "Mean", "Std. dev.", "r with quality"], rows,
            [2016, 2160, 1008, 1008, 1008, 1080, 1296], align=["left", "left", "right", "right", "right", "right", "center"], sz=19)
    cc = R.class_counts
    r.para(f"The six grades are strongly imbalanced (Figure [[f_classes]]). Grades 5 and 6 hold {int(cc[5]):,} and {int(cc[6]):,} "
           f"wines – {100 * (cc[5] + cc[6]) / R.N:.1f} % together – while grade 3 has only {int(cc[3])} wines, grade 8 {int(cc[8])} and "
           f"grade 4 {int(cc[4])}. In a 10-fold split a test fold therefore holds about one wine of grade 3 and two of grade 8, which is "
           "the main difficulty of the task.")
    r.figure("f_classes", FIG / "class_distribution.png", "Number of wines per quality grade (the two majority grades in light colour)", 5.6)

    r.h2("Exploratory Data Analysis")
    r.para("Figure [[f_bygrade]] shows how four measurements change with the grade. Alcohol rises clearly from grade 5 upwards, "
           "volatile acidity falls, and sulphates and citric acid rise; the boxes of neighbouring grades overlap widely, however, so no "
           "single measurement separates the grades. Figure [[f_corr]] gives all pairwise correlations. Alcohol has the strongest "
           f"correlation with quality (r = {R.pearson['alcohol']:+.2f}), followed by volatile acidity ({R.pearson['volatile acidity']:+.2f}), "
           f"sulphates ({R.pearson['sulphates']:+.2f}) and citric acid ({R.pearson['citric acid']:+.2f}) – the four attributes the base "
           "paper highlights. Several inputs are correlated with each other (fixed acidity with citric acid, density and pH; free with "
           "total sulphur dioxide), which matters later when importance is measured by shuffling one feature at a time.")
    r.figure("f_bygrade", FIG / "features_by_grade.png", "Four measurements by quality grade", 6.6)
    r.figure("f_corr", FIG / "correlation_heatmap.png", "Pearson correlation between the 11 measurements and quality", 5.4)

    r.h2("Data Preprocessing")
    r.h3("Classes and Duplicate Rows")
    r.para("No grade is dropped or merged: the task keeps all six grades, exactly as the paper's tables do (grades 0–2, 9 and 10 never "
           f"occur). The {R.n_duplicates} exact duplicate rows are kept as well, because the paper uses all {R.N:,} wines; a duplicate can "
           "fall into a training and a test fold at the same time, which slightly favours every model equally and does not change the "
           "comparison between them.")
    r.h3("Min–Max Normalisation")
    r.para("Following the paper, every feature is rescaled linearly to [0, 1] with (2.1), so that measurements in different units "
           "contribute comparably to the distance-based SVM and to the neural network.")
    r.eqs([("e_minmax", r"x_{ij}' = \frac{x_{ij} - \min_{i} x_{ij}}{\max_{i} x_{ij} - \min_{i} x_{ij}}")])
    r.h3("Preventing Data Leakage")
    r.para("If the minimum and maximum in (2.1) are computed on all the data before cross-validation, the test folds influence the "
           "scaling of the training data. In this project the scaler is the first step of a scikit-learn Pipeline {c:pedregosa2011} "
           "together with the learner, so in every fold it is fitted on the training wines only and merely applied to the test wines. "
           "The same rule is used in Review 2 for SMOTE, for feature selection and for every choice of a setting: anything learned from "
           "data is learned inside the training fold.")

    r.h2("Evaluation Protocol")
    r.para("The paper evaluates its models with 10-fold cross-validation over 100 experiments. Here this is implemented as stratified "
           "10-fold cross-validation repeated 10 times with different shuffles (seeds 0–9): every wine is predicted once per repeat by "
           "a model that did not see it, giving 10 × 1,599 = 15,990 out-of-fold predictions per model. The metrics are computed on these "
           "pooled predictions. All learners are scored on the same folds in each repeat, which the diversity weight of the paper needs "
           "(it compares error vectors wine by wine) and which allows paired comparisons between models (Section [[s_paired]]). "
           "Table [[t_protocol]] lists the settings.")
    r.table("t_protocol", "Evaluation protocol",
            ["Setting", "Value"],
            [["Cross-validation", "stratified 10-fold, repeated 10 times (fold seeds 0–9) = 100 fold-runs"],
             ["Predictions per model", "15,990 out-of-fold predictions (each wine 10 times)"],
             ["Preprocessing", "min–max scaling (and SMOTE, feature selection) fitted inside each training fold"],
             ["Model seeds", "random_state = 42 for every learner"],
             ["Primary metric, Review 1", "overall accuracy, as in the paper"],
             ["Primary metric, Review 2", "macro-F1, fixed in the code before any Review-2 experiment was run"]],
            [3024, 6336])

    r.h2("Evaluation Metrics", key="s_metrics")
    r.para("For class k, TP<sub>k</sub> counts the wines of class k predicted as k, FP<sub>k</sub> the wines of other classes predicted "
           "as k and FN<sub>k</sub> the wines of class k predicted as something else {c:sokolova2009}. The metrics are defined in "
           "(2.2)–(2.7).")
    r.eqs([("e_acc", r"\text{Accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}\left[\hat{y}_{i} = y_{i}\right]"),
           ("e_prec", r"P_{k} = \frac{TP_{k}}{TP_{k} + FP_{k}}"),
           ("e_rec", r"R_{k} = \frac{TP_{k}}{TP_{k} + FN_{k}}"),
           ("e_f1", r"F1_{k} = \frac{2\,P_{k}\,R_{k}}{P_{k} + R_{k}}"),
           ("e_macro", r"\text{Macro-F1} = \frac{1}{K}\sum_{k=1}^{K} F1_{k}"),
           ("e_bal", r"\text{Balanced accuracy} = \frac{1}{K}\sum_{k=1}^{K} R_{k}")])
    r.para("Accuracy (2.2) is dominated by grades 5 and 6. Macro-F1 (2.6) and balanced accuracy (2.7) give every grade the same "
           "weight, so they show whether the rare grades are recognised at all; this is why macro-F1 is the primary metric of Review 2.")
    r.para("**A note on terminology.** The paper calls its per-class metric \"precision\", but its own worked example divides the "
           "correct predictions of a class by the number of wines that truly belong to it – that is TP/(TP + FN), the recall (2.4). "
           f"Recomputing the paper's per-class values from its confusion matrix confirms this: {int(R.t9['n_per_class_matching_column_wise'])} "
           "of the 6 values reproduce when divided by the true-class totals and only one when divided by the predicted totals. The per-class "
           "comparisons with the paper in this report therefore use recall, under the paper's definition; conventional precision is "
           "reported separately.")


def chapter3(r):
    r.chapter("MODELS")
    r.h2("Overview of the Base Learners")
    r.para("Table [[t_learners]] lists the four base learners. SVM and Random Forest are those of the paper. The RNN and the ELM are "
           "neural models outside the classical machine-learning scope of the course, so each is replaced by the closest classical "
           "learner: Gradient Boosting, which, like a recurrent model, refines its prediction step by step, and a multilayer perceptron, "
           "which is a neural network like the ELM but trained by back-propagation. Every learner is a Pipeline of a min–max scaler and "
           "the classifier, and every learner outputs class probabilities, which the soft vote of the ensemble needs.")
    r.table("t_learners", "The four base learners of the reproduction",
            ["Paper's learner", "Our learner", "Main settings", "Reason"],
            [["SVM", "SVC (RBF kernel)", "C = 10, γ = 'scale', balanced class weights, Platt-calibrated probabilities", "as in the paper"],
             ["Random Forest", "RandomForestClassifier", "300 trees, balanced class weights per bootstrap sample", "as in the paper"],
             ["RNN", "GradientBoostingClassifier", "200 boosting stages, depth-3 trees, learning rate 0.1", "RNN is outside the course scope"],
             ["ELM", "MLPClassifier", "hidden layers (64, 32), ReLU, Adam, up to 2,000 iterations", "ELM is outside the course scope"]],
            [1584, 2448, 3600, 2016], sz=19)

    r.h2("Support Vector Machine")
    r.para("An SVM {c:cortes1995} separates two classes with the hyperplane of maximum margin in a feature space defined by a kernel. "
           "Its decision function (3.1) is a weighted sum of kernel values between the wine and the support vectors, with the RBF kernel "
           "(3.2). The six grades are handled one-against-one. Because the ensemble needs probabilities, the SVM is wrapped in a calibration "
           "step (Platt scaling) that is fitted by an internal cross-validation on the training fold only.")
    r.eqs([("e_svm", r"f(x) = \operatorname{sign}\left(\sum_{i} \alpha_{i}\, y_{i}\, K\left(x_{i}, x\right) + b\right)"),
           ("e_rbf", r"K\left(x, x'\right) = \exp\left(-\gamma \left\| x - x' \right\|^{2}\right)")])

    r.h2("Random Forest")
    r.para("A Random Forest {c:breiman2001} grows B decision trees, each on a bootstrap sample of the training wines and with a random "
           "subset of features tried at every split. The class probabilities are the average of the trees' probabilities (3.3). With "
           "B = 300 and balanced class weights recomputed on every bootstrap sample, it is the strongest single learner of the reproduction.")
    r.eqs([("e_rf", r"\hat{p}\left(k \mid x\right) = \frac{1}{B}\sum_{b=1}^{B} \hat{p}_{b}\left(k \mid x\right)")])

    r.h2("Gradient Boosting")
    r.para("Gradient Boosting {c:friedman2001} builds an additive model stage by stage: each new set of small trees h<sub>m</sub> is fitted to the "
           "negative gradient of the loss of the current model and added with a learning rate η (3.4). It stands in for the paper's RNN "
           "because both improve their prediction iteratively; it is not a sequence model, which this tabular task does not need.")
    r.eqs([("e_gb", r"F_{m}(x) = F_{m-1}(x) + \eta\, h_{m}(x)")])

    r.h2("Multilayer Perceptron")
    r.para("The multilayer perceptron has two hidden layers of 64 and 32 ReLU units and a softmax output (3.5), trained by "
           "back-propagation {c:rumelhart1986} with the Adam optimiser. The ELM of the paper {c:huang2006} has the same feed-forward shape but "
           "fixes random hidden weights and solves only the output layer in closed form; the MLP is the closest classical alternative. Early "
           "stopping is not used, because it would set aside a validation slice from a training fold that contains only nine grade-3 wines.")
    r.eqs([("e_mlp", r"\hat{p}(x) = \operatorname{softmax}\left(W_{3}\, \operatorname{ReLU}\left(W_{2}\, \operatorname{ReLU}\left(W_{1} x' + b_{1}\right) + b_{2}\right) + b_{3}\right)")])

    r.h2("The Weighted Ensemble of the Base Paper", key="s_ensemble")
    r.para("The ensemble of the paper combines the M = 4 learners with weights that reward accuracy and diversity. Written in this "
           "report's notation, the steps are (3.6)–(3.13); the paper's own equation number is given in brackets. The weights are computed "
           "in each repeat from the out-of-fold predictions of that repeat, so they use exactly the information the paper describes.")
    r.para("**Combination (paper's Eq. 1).** The ensemble output is the weighted sum of the learners' outputs (3.6). Read literally, the "
           "outputs are class-probability vectors, giving a soft vote; read as one-hot labels, it becomes a weighted majority (hard) vote "
           "(3.7). The paper does not say which reading it uses, so both are implemented; the soft vote is the headline.")
    r.eqs([("e_soft", r"\hat{p}(x) = \sum_{m=1}^{M} w_{m}\, p_{m}(x), \qquad \hat{y} = \arg\max_{k}\, \hat{p}_{k}(x)"),
           ("e_hard", r"\hat{y} = \arg\max_{k} \sum_{m=1}^{M} w_{m}\, \mathbb{1}\left[\hat{y}^{(m)} = k\right]")])
    r.para("**Accuracy weight (paper's Eqs. 3, 5 and 6).** An indicator marks each wrong prediction (3.8), the cross-validated error of "
           "a learner is the mean of its indicators (3.9), and the accuracy weight is the normalised inverse error (3.10).")
    r.eqs([("e_g", r"g\left(\hat{y}_{i}^{(m)}, y_{i}\right) = \begin{cases} 0, & \hat{y}_{i}^{(m)} = y_{i} \\ 1, & \text{otherwise} \end{cases}"),
           ("e_err", r"\varepsilon_{m} = \frac{1}{N}\sum_{i=1}^{N} g\left(\hat{y}_{i}^{(m)}, y_{i}\right)"),
           ("e_wacc", r"w_{m}^{acc} = \frac{1/\varepsilon_{m}}{\sum_{j=1}^{M} 1/\varepsilon_{j}}")])
    r.para("**Diversity weight (paper's Eqs. 7–9).** The indicators of a learner over all wines form its error vector (3.11). Its "
           "diversity is the sum of the Euclidean distances to the error vectors of the other learners (3.12), normalised in (3.13).")
    r.eqs([("e_evec", r"e_{m} = \left(g\left(\hat{y}_{1}^{(m)}, y_{1}\right), \ldots, g\left(\hat{y}_{N}^{(m)}, y_{N}\right)\right)"),
           ("e_D", r"D_{m} = \sum_{j \neq m} \left\| e_{m} - e_{j} \right\|_{2}"),
           ("e_wdiv", r"w_{m}^{div} = \frac{D_{m}}{\sum_{j=1}^{M} D_{j}}")])
    r.para("**Final weight (paper's Eq. 4).** The final weight is the average of the two (3.14); the weights sum to one.")
    r.eqs([("e_w", r"w_{m} = \frac{1}{2}\left(w_{m}^{acc} + w_{m}^{div}\right)")])
    r.para("A property of (3.10) and (3.13) is worth stating now, because it explains the results of Chapter 4. Both normalise quantities "
           "that differ little between reasonable learners: error rates of 29 % and 38 % give inverse errors of 3.4 and 2.6, and the "
           "distances between error vectors are of similar size. The weights therefore stay close to the uniform 1/M = 0.25, and the "
           "ensemble behaves almost like a plain average of its members.")

    r.h2("Class Balancing Schemes")
    r.para("Review 1 already used balanced class weights in SVM and Random Forest, but not in the other two learners. Review 2 compares "
           "four schemes on the same four learners and the same weighted vote, so that balancing is the only thing that changes "
           "{c:he2009}:")
    r.numbered([
        "**No balancing** – every wine has the same weight.",
        "**Review 1 (partial)** – balanced class weights in SVM and Random Forest only.",
        "**Class weights, all four** – balanced weights in every learner. Gradient Boosting and the MLP have no class-weight option, "
        "so they receive the equivalent per-sample weights (3.15) through a small wrapper, computed from the training fold.",
        "**SMOTE** {c:chawla2002} – synthetic wines of the rare grades are created inside each training fold, after scaling, by "
        "interpolating between a wine and one of its five nearest neighbours of the same grade (3.16), until every grade is as large "
        "as the largest. The test fold is never resampled. The imbalanced-learn library {c:lemaitre2017} provides the implementation.",
    ])
    r.eqs([("e_sw", r"s_{i} = \frac{N}{K\, n_{y_{i}}}"),
           ("e_smote", r"x_{new} = x_{i} + \lambda\left(x_{nn} - x_{i}\right), \qquad \lambda \sim U(0, 1)")])

    r.h2("Weight Sharpening with a Temperature", key="s_temp")
    r.para("To test the explanation that the weights are too flat, a temperature T is introduced into (3.10) and (3.13): the inverse "
           "errors and the diversities are raised to the power T before normalising, (3.17) and (3.18), and (3.14) is unchanged. T = 1 "
           "is exactly the paper; a larger T moves weight towards the most accurate (or most diverse) learner. Two variants are tried: "
           "sharpening only the accuracy term, and sharpening both. This sweep is a diagnostic only: its weights are computed from the "
           "same out-of-fold predictions on which it is scored, so it is never used to select a model.")
    r.eqs([("e_tacc", r"w_{m}^{acc}(T) = \frac{\varepsilon_{m}^{-T}}{\sum_{j=1}^{M} \varepsilon_{j}^{-T}}"),
           ("e_tdiv", r"w_{m}^{div}(T) = \frac{D_{m}^{\,T}}{\sum_{j=1}^{M} D_{j}^{\,T}}")])

    r.h2("Learned Temperature")
    r.para("The proper way to use the temperature is to choose it without the test fold. The learned-temperature ensemble does this "
           "inside every outer training fold:")
    r.numbered([
        "split the training fold into 5 inner folds and collect out-of-fold probabilities of the four learners;",
        "for every T ∈ {1, 2, 5, 10, 25, 100} and both variants, compute the weights (3.17)–(3.18) and score the weighted vote on the "
        "inner predictions with macro-F1;",
        "keep the best setting (ties go to the smaller T, that is, towards the paper);",
        "refit the four learners on the whole training fold and predict the outer test fold with the chosen weights.",
    ])
    r.para("The outer test fold therefore never influences the choice of T, and the result is an honest estimate.")

    r.h2("Stacking and Stronger Members")
    r.para("Two further ideas are tested. **Stacking** {c:wolpert1992} replaces the hand-built weights with a learned combiner: a "
           "multinomial logistic regression is trained on the members' out-of-fold class probabilities (3.19), using an inner 5-fold split. "
           "A second version gives the combiner balanced class weights. **Stronger members** replace the two weakest learners by "
           "ExtraTrees {c:geurts2006} (500 extremely randomised trees) and histogram-based Gradient Boosting, a fast gradient-boosting "
           "variant in the style of LightGBM {c:ke2017}, both class-weighted. Table [[t_candidates]] lists all candidates of Review 2.")
    r.eqs([("e_stack", r"\hat{p}(x) = \operatorname{softmax}\left(\beta_{0} + B\left[p_{1}(x);\, p_{2}(x);\, \ldots;\, p_{M}(x)\right]\right)")])
    r.table("t_candidates", "Candidate models of Review 2",
            ["Group", "Candidates", "What is learned inside the training fold"],
            [["A. Balancing", "4 learners and the paper's ensemble × {none, Review 1, class weights, SMOTE}", "scaler, SMOTE samples, weights (3.14)"],
             ["B1. Sharpening", "paper's ensemble with T = 1 … 100 (diagnostic only)", "– (weights from the scored predictions)"],
             ["B2. Learned T", "learned-temperature ensemble with Review-1 members and with SMOTE members", "T and variant by inner 5-fold CV"],
             ["B3. Stacking", "logistic-regression combiner on the 4 learners; balanced combiner; on SVM + RF + ExtraTrees + HistGB", "combiner by inner 5-fold CV"],
             ["B3. Members", "ExtraTrees, HistGB, and the paper's weights on SVM + RF + ExtraTrees + HistGB", "scaler, trees"]],
            [1872, 4464, 3312], sz=19)

    r.h2("Feature Importance Methods", key="s_fimethods")
    r.para("Three measures are computed and compared, because each has known weaknesses:")
    r.bullets([
        "**Permutation importance** (primary measure) {c:breiman2001}, {c:fisher2019} – the drop in macro-F1 on the held-out fold when "
        "one feature is shuffled (3.20), averaged over 20 shuffles and the 10 folds. It measures what the model actually uses on unseen "
        "wines, but it shares the credit between correlated features.",
        "**Mean decrease in impurity (MDI)** of the Random Forest – how much the splits on a feature reduce impurity. It is free but "
        "biased towards continuous features with many distinct values {c:strobl2007}.",
        "**Spearman rank correlation** (3.21) of each feature with quality – the direction of the effect (higher alcohol, better wine), "
        "which the other two measures do not give.",
    ])
    r.eqs([("e_perm", r"I_{j} = S\left(f, X_{test}\right) - \frac{1}{R}\sum_{r=1}^{R} S\left(f, X_{test}^{(j,r)}\right)"),
           ("e_spear", r"\rho = 1 - \frac{6\sum_{i=1}^{N} d_{i}^{2}}{N\left(N^{2} - 1\right)}")])
    r.para("Finally, to find how many laboratory tests are needed, Random Forest is retrained on the top-k features for k = 1, 2, 3, 4, "
           "6, 8 and 11. The ranking used to choose the features is recomputed inside every training fold, so the test fold never "
           "influences which features are kept.")


def chapter4(r):
    r.chapter("EVALUATION AND RESULTS")
    a = R.acc
    r.h2("Review 1: Model Ranking")
    r.para("Table [[t_rank]] and Figure [[f_rank]] give the overall accuracy of every model over the 100 fold-runs, next to the values "
           "published in the paper.")
    paper_a = R.C.MA_2024_BASE_LEARNER_ACCURACY
    r.table("t_rank", "Overall accuracy (%): Reference Paper Result vs Our Reproduction Result",
            ["Model (paper's learner)", "Reference Paper Result", "Our Reproduction Result", "Our rank"],
            [["Random Forest", f2(paper_a["RF"]), f2(a["RF"]), "1"],
             ["Weighted ensemble, hard vote", "–", f2(a["Ensemble (hard vote)"]), "2"],
             ["**Weighted ensemble, soft vote**", "**89.73**", f"**{f2(a['Ensemble (soft vote)'])}**", "3"],
             ["Gradient Boosting (RNN)", f2(paper_a["RNN"]), f2(a["GradBoost"]), "4"],
             ["SVM", f2(paper_a["SVM"]), f2(a["SVM"]), "5"],
             ["MLP (ELM)", f2(paper_a["ELM"]), f2(a["MLP"]), "6"]],
            [3600, 2016, 2160, 1296], align=["left", "center", "center", "center"])
    r.figure("f_rank", FIG / "model_ranking.png", "Overall accuracy of the six models (the soft-vote ensemble dark, Random Forest gold)", 5.6)
    r.para(f"**The central claim of the paper does not reproduce.** The paper's ensemble beats its best learner by 9.02 points; ours "
           f"reaches {f2(a['Ensemble (soft vote)'])} % and stays {f2(a['RF'] - a['Ensemble (soft vote)'])} points *below* Random Forest. "
           "It does beat the other three learners, which is what an average of one strong and three weaker members does. The hard vote "
           f"({f2(a['Ensemble (hard vote)'])} %) is slightly higher than the soft vote overall; the soft vote is kept as the headline "
           "because it is the literal reading of the paper's equation, not because it scores higher. Section [[s_why]] explains the gap.")

    r.h2("Per-Class Comparison with the Base Paper")
    me = R.metrics["Ensemble"]
    mrf = R.metrics["RF"]
    rows = []
    for k, c in enumerate(R.CLASSES):
        rows.append([str(c), str(int(R.class_counts[c])), f2(R.C.CORTEZ_2009_PER_CLASS_PRECISION[k]), f2(R.C.MA_2024_PER_CLASS_PRECISION[k]),
                     f2(me.loc[c, "sensitivity_recall"]), f2(mrf.loc[c, "sensitivity_recall"])])
    rows.append(["Overall", f"{R.N:,}", "–", "89.73", f2(a["Ensemble (soft vote)"]), f2(a["RF"])])
    r.para("Table [[t_perclass]] compares the per-class results under the paper's definition (recall, Section [[s_metrics]]). The shape "
           "of the paper's finding reproduces: grades 5 and 6 are predicted far better than in Cortez et al., and the extreme grades "
           "remain the hardest. The rare grades, however, are almost never recognised: grade 3 at 0 %, grade 4 at "
           f"{f2(me.loc[4, 'sensitivity_recall'])} % and grade 8 at {f2(me.loc[8, 'sensitivity_recall'])} %. With ten grade-3 wines "
           "spread over ten folds, each test fold holds about one of them.")
    r.table("t_perclass", "Per-class recall (%) – the paper's \"precision\": benchmark, Reference Paper Result and Our Reproduction Result",
            ["Grade", "Wines", "Cortez et al. (2009)", "Reference Paper Result", "Our ensemble", "Our Random Forest"], rows,
            [1152, 1152, 1872, 2016, 1584, 1872], align=["center"] * 6, bold_rows=(6,))
    rows = []
    for c in R.CLASSES:
        rows.append([str(c), f"{int(me.loc[c, 'n_actual']):,}", f2(me.loc[c, "precision"]), f2(me.loc[c, "sensitivity_recall"]),
                     f2(me.loc[c, "specificity"])])
    r.para("Table [[t_conv]] gives the conventional precision, recall and specificity of the ensemble on the pooled predictions, and "
           "Figure [[f_cm]] the pooled confusion matrices. Most errors fall into the neighbouring grade, and the rare grades are absorbed "
           "by grades 5 and 6.")
    r.table("t_conv", "Our Reproduction Result: conventional per-class metrics of the soft-vote ensemble (%, pooled predictions)",
            ["Grade", "Predictions (10 × wines)", "Precision", "Recall", "Specificity"], rows,
            [1440, 2448, 1872, 1872, 1872], align=["center"] * 5)
    r.figure("f_cm", FIG / "confusion_matrices.png", "Pooled confusion matrices of the Review-1 ensemble, the Review-1 Random Forest and the best Review-2 model", 6.6)

    r.h2("Learned Weights and the Paper's Weights")
    w = R.our_weights
    pw = R.C.MA_2024_TABLE8_WEIGHT_SUM
    r.para("Table [[t_weights]] and Figure [[f_weights]] compare the final weights (3.14). Ours never differ from the uniform 0.25 by "
           f"more than {max(abs(v - 0.25) for v in w.values()):.3f}; the paper's never by more than "
           f"{max(abs(v - 0.25) for v in pw.values()):.3f}. In both cases the scheme of Section [[s_ensemble]] produces nearly equal weights.")
    r.table("t_weights", "Final ensemble weights: Reference Paper Result (Table 8 of the paper) vs Our Reproduction Result (mean of 10 repeats)",
            ["Learner (paper's learner)", "Reference Paper Result", "Our Reproduction Result"],
            [["SVM", f"{pw['SVM']:.4f}", f"{w['SVM']:.4f}"], ["Random Forest", f"{pw['RF']:.4f}", f"{w['RF']:.4f}"],
             ["Gradient Boosting (RNN)", f"{pw['RNN']:.4f}", f"{w['GradBoost']:.4f}"], ["MLP (ELM)", f"{pw['ELM']:.4f}", f"{w['MLP']:.4f}"]],
            [3600, 2880, 2880], align=["left", "center", "center"])
    r.figure("f_weights", FIG / "weights_vs_paper.png", "Final weights of the four learners: our reproduction and the paper's Table 8", 5.6)

    r.h2("Why 89.73 % Does Not Reproduce", key="s_why")
    r.para("Two checks, computed in code from the numbers printed in the paper, show that the published figures cannot be reconciled "
           "with each other. They are reported as figures we *could not reconcile*, not as a claim that the paper is wrong; the paper's "
           "confusion matrix was transcribed by eye from the printed table and may contain reading errors.")
    r.para("**(a) The confusion matrix implies a different protocol and accuracy.** The cells of the paper's ensemble confusion matrix "
           f"(its Table 9) add up to {int(R.t9['implied_test_set_size'])} wines – {f2(R.t9['implied_fraction_of_dataset_pct'])} % of the "
           "data, that is a single hold-out split rather than 100 cross-validation runs over all wines. Its diagonal holds "
           f"{int(R.t9['correct_predictions_on_diagonal'])} correct predictions, an accuracy of {f2(R.t9['implied_overall_accuracy_pct'])} % – "
           f"{f2(R.t9['discrepancy_pct_points'])} points below the 89.73 % stated in the text (Table [[t_t9]]).")
    r.table("t_t9", "Check (a): what the paper's own confusion matrix implies",
            ["Quantity", "Value"],
            [["Wines in the confusion matrix", f"{int(R.t9['implied_test_set_size'])}"],
             ["Share of the 1,599 wines", f"{f2(R.t9['implied_fraction_of_dataset_pct'])} %"],
             ["Correct predictions (diagonal)", f"{int(R.t9['correct_predictions_on_diagonal'])}"],
             ["Accuracy implied by the matrix", f"{f2(R.t9['implied_overall_accuracy_pct'])} %"],
             ["Accuracy reported in the text", "89.73 %"],
             ["Difference", f"{f2(R.t9['discrepancy_pct_points'])} points"],
             ["Per-class values reproduced column-wise (recall)", f"{int(R.t9['n_per_class_matching_column_wise'])} of 6"]],
            [5760, 3600], align=["left", "center"])
    rows = [[str(int(x.class_)), f2(x.paper_reported_pct), f2(x.recomputed_column_wise_pct), f2(x.recomputed_row_wise_pct),
             "yes" if x.column_wise_matches else "no"] for x in R.t9_class.rename(columns={"class": "class_"}).itertuples()]
    r.table("t_t9class", "Per-class values of the paper recomputed from its confusion matrix (%)",
            ["Grade", "Reported in the paper", "Divided by true totals (recall)", "Divided by predicted totals (precision)", "Matches"], rows,
            [1152, 2016, 2448, 2592, 1296], align=["center"] * 5, sz=19)
    r.para("**(b) The paper's weights and base accuracies imply about 67.5 %.** Applying the paper's final weights to its own base "
           f"accuracies gives a weighted average of {f2(R.cons['weighted_average_of_base_accuracies_pct'])} % (Table [[t_cons]]). A voting "
           "ensemble can legitimately exceed this average when its members err on different wines, so this is an indicative reference "
           f"point, not a proof. But the paper's ensemble sits {f2(R.cons['gap_vs_weighted_average_pct_points'])} points above it, while ours "
           f"sits {f2(R.cons['our_gap_vs_their_weighted_average_pct_points'])} points above it.")
    r.table("t_cons", "Check (b): the paper's weights applied to its own base accuracies",
            ["Quantity", "Value"],
            [["Largest deviation of the paper's weights from 0.25", f"{R.cons['max_abs_deviation_from_uniform_weight']:.3f}"],
             ["Best single learner in the paper (RF)", f"{f2(R.cons['best_single_base_learner_pct'])} %"],
             ["Weighted average of the paper's base accuracies", f"{f2(R.cons['weighted_average_of_base_accuracies_pct'])} %"],
             ["Paper's reported ensemble accuracy", "89.73 %"],
             ["Gap: paper's ensemble – weighted average", f"+{f2(R.cons['gap_vs_weighted_average_pct_points'])} points"],
             ["Our ensemble", f"{f2(R.cons['our_ensemble_pct'])} %"],
             ["Gap: our ensemble – the paper's weighted average", f"+{f2(R.cons['our_gap_vs_their_weighted_average_pct_points'])} points"]],
            [5760, 3600], align=["left", "center"])
    r.para("These checks also explain our own ranking. With weights this close to uniform, the ensemble approximates an unweighted "
           "average of its members, and an average of one strong learner and three weaker ones lands between them – above the three "
           "weaker learners and below the strongest, exactly as in Table [[t_rank]]. Published accuracies for the six-grade red-wine task "
           f"are typically in the low 60s to low 70s per cent; our {f2(a['Ensemble (soft vote)'])} % lies in that range and 89.73 % well above it.")

    # ---------------- Review 2 ----------------
    r.h2("Review 2: Class Balancing")
    b = R.balancing
    ens = b[b["model"] == "Ensemble (paper weights)"]
    rows = []
    for x in ens.itertuples():
        rows.append([x.balancing_label, f2(x.accuracy), f2(x.balanced_accuracy), f2(x.macro_f1)] +
                    [f"{getattr(x, f'recall_{c}'):.1f}" for c in R.CLASSES])
    smote = ens[ens["balancing"] == "smote"].iloc[0]
    part = ens[ens["balancing"] == "partial"].iloc[0]
    r.para("Table [[t_bal]] applies the four balancing schemes to the paper's ensemble. Balancing moves recall from the two majority "
           "grades to the rare ones. With SMOTE, grade-4 recall rises from "
           f"{f2(part['recall_4'])} % to {f2(smote['recall_4'])} %, grade 3 from 0 % to {f2(smote['recall_3'])} % and grade 7 from "
           f"{f2(part['recall_7'])} % to {f2(smote['recall_7'])} %, and macro-F1 from {f2(part['macro_f1'])} to {f2(smote['macro_f1'])}; "
           f"accuracy falls by {f2(part['accuracy'] - smote['accuracy'])} points, because more wines of grades 5 and 6 are now assigned "
           "to the rare grades. This is the trade-off balancing is meant to make, and it is the reason accuracy alone cannot judge it.")
    r.table("t_bal", "Class balancing applied to the paper's ensemble (%)",
            ["Scheme", "Accuracy", "Bal. acc.", "Macro-F1", "R₃", "R₄", "R₅", "R₆", "R₇", "R₈"], rows,
            [2448, 1008, 1008, 1008, 720, 720, 720, 720, 720, 720], align=["left"] + ["center"] * 9, sz=19)
    piv = b.pivot_table(index="model", columns="balancing", values="macro_f1")
    order = ["SVM", "RF", "GradBoost", "MLP", "Ensemble (paper weights)"]
    names = {"SVM": "SVM", "RF": "Random Forest", "GradBoost": "Gradient Boosting", "MLP": "MLP",
             "Ensemble (paper weights)": "Paper's ensemble"}
    rows = [[names[m]] + [f2(piv.loc[m, s]) for s in ("none", "partial", "class_weight", "smote")] for m in order]
    r.para("Table [[t_balf1]] shows the macro-F1 of every learner under every scheme. SMOTE helps every learner, most of all SVM and "
           "Gradient Boosting; class weights help the ensemble and Gradient Boosting but hurt the MLP, whose training becomes unstable "
           "when ten wines of grade 3 carry the weight of several hundred. Figure [[f_bal]] shows the per-class recalls.")
    r.table("t_balf1", "Macro-F1 of every learner under every balancing scheme",
            ["Model", "No balancing", "Review 1 (partial)", "Class weights, all four", "SMOTE"], rows,
            [2592, 1584, 1872, 2160, 1440], align=["left"] + ["center"] * 4)
    r.figure("f_bal", F2 / "A_class_balancing.png", "Effect of the four balancing schemes on accuracy, macro-F1 and per-class recall", 6.4)

    r.h2("Review 2: Improving the Result")
    r.h3("Testing the Review-1 Diagnosis")
    t = R.temp[R.temp["balancing"] == "partial"]
    ta = t[t["sharpen"] == "accuracy"].set_index("temperature")
    tb = t[t["sharpen"] == "both"].set_index("temperature")
    rows = [[str(T), f2(ta.loc[T, "accuracy"]), f"{ta.loc[T, 'largest_weight']:.3f}", f2(tb.loc[T, "accuracy"]), f2(tb.loc[T, "macro_f1"])]
            for T in R.C.WEIGHT_TEMPERATURES]
    first_over = next((T for T in R.C.WEIGHT_TEMPERATURES if ta.loc[T, "accuracy"] > a["RF"]), None)
    r.para("Review 1 attributed the ensemble's failure to beat Random Forest to its near-uniform weights. Table [[t_tsweep]] and "
           "Figure [[f_tsweep]] test this with the temperature of Section [[s_temp]]. As T grows, the weight moves to Random Forest and the "
           f"ensemble accuracy rises; sharpening the accuracy term overtakes Random Forest ({f2(a['RF'])} %) from T = {first_over}. "
           "Sharpening the diversity term as well eventually backfires: it moves weight to the learner whose errors differ most from the "
           "others, which is usually the weakest. The diagnosis therefore holds – but this sweep is scored on the same predictions it is "
           "computed from, so it is only a test, not a model.")
    r.table("t_tsweep", "Weight sharpening of the Review-1 ensemble (diagnostic only)",
            ["T", "Accuracy, accuracy term sharpened (%)", "Largest weight", "Accuracy, both terms sharpened (%)", "Macro-F1, both terms"], rows,
            [864, 2592, 1584, 2592, 1872], align=["center"] * 5, sz=19)
    r.figure("f_tsweep", F2 / "B1_weight_temperature.png", "Ensemble accuracy against the temperature T (T = 1 is the paper)", 6.4)

    r.h3("Learned Temperature")
    sp, subp = R.share_sharp("partial")
    ss, subs = R.share_sharp("smote")
    rows = [["Review-1 members", f2(g(R.LT_R1, "accuracy")), f2(g(R.LT_R1, "macro_f1")), f2(g(R.ENS_R1, "accuracy")), f2(g(R.ENS_R1, "macro_f1")),
             f"{sp:.0f} %"],
            ["SMOTE members", f2(g(R.LT_SMOTE, "accuracy")), f2(g(R.LT_SMOTE, "macro_f1")), f2(g(R.ENS_SMOTE, "accuracy")), f2(g(R.ENS_SMOTE, "macro_f1")),
             f"{ss:.0f} %"]]
    r.para("Choosing T inside each training fold (Table [[t_learned]]) turns the diagnosis into an honest improvement. With the "
           f"reproduction's own members, accuracy rises from {f2(g(R.ENS_R1, 'accuracy'))} % to {f2(g(R.LT_R1, 'accuracy'))} % and macro-F1 "
           f"from {f2(g(R.ENS_R1, 'macro_f1'))} to {f2(g(R.LT_R1, 'macro_f1'))}; the inner cross-validation chose a sharp temperature (T ≥ 10) "
           f"in {sp:.0f} % of the 100 folds (Figure [[f_chosen]]). With SMOTE members it reaches a macro-F1 of {f2(g(R.LT_SMOTE, 'macro_f1'))}.")
    r.table("t_learned", "Learned-temperature ensemble against the paper's weights (T = 1)",
            ["Members", "Learned T: accuracy", "Learned T: macro-F1", "Paper: accuracy", "Paper: macro-F1", "Folds with T ≥ 10"], rows,
            [2016, 1584, 1584, 1440, 1440, 1584], align=["left"] + ["center"] * 5, sz=19)
    r.figure("f_chosen", F2 / "B4_chosen_temperatures.png", "Temperature chosen by the inner cross-validation of each training fold", 5.4)

    r.h3("Stacking and Stronger Members")
    r.para(f"A logistic-regression combiner on the four learners reaches {f2(g(R.STACK4, 'accuracy'))} % accuracy but only "
           f"{f2(g(R.STACK4, 'macro_f1'))} macro-F1: trained to maximise likelihood on imbalanced data, it relearns the majority-grade "
           f"bias. Its class-balanced version swings the other way ({f2(g(R.STACK_BAL, 'accuracy'))} % accuracy, the highest balanced "
           f"accuracy of all at {f2(g(R.STACK_BAL, 'balanced_accuracy'))} %, with {f2(g(R.STACK_BAL, 'recall_3'))} % recall on grade 3 and "
           f"{f2(g(R.STACK_BAL, 'recall_8'))} % on grade 8). ExtraTrees alone ({f2(g('ExtraTrees', 'accuracy'))} %) is as accurate as "
           f"Random Forest, and the paper's weights on SVM + RF + ExtraTrees + HistGB give {f2(g(R.PAPER_STRONG, 'accuracy'))} %.")

    r.h3("All Candidates")
    rows = []
    for x in R.comp.itertuples():
        rows.append([str(x.rank_by_macro_f1), R.nice_model(x.model), x.kind, f2(x.accuracy), f2(x.balanced_accuracy), f2(x.macro_f1)])
    r.para("Table [[t_all]] ranks all 28 candidates by the primary metric, and Figure [[f_tradeoff]] plots accuracy against macro-F1. "
           f"No candidate is best on both. The best macro-F1 comes from **Random Forest with SMOTE** ({f2(g(R.RF_SMOTE, 'macro_f1'))}), "
           f"followed closely by the learned-temperature ensemble with SMOTE ({f2(g(R.LT_SMOTE, 'macro_f1'))}); the best accuracy is "
           f"still Random Forest without resampling ({f2(a['RF'])} %). The dashed line in Figure [[f_tradeoff]] joins the models that no "
           "other model beats on both metrics.")
    r.figure("f_tradeoff", F2 / "B_tradeoff.png", "Accuracy against macro-F1 for every candidate; the dashed line is the best trade-off frontier", 6.0)
    r.table("t_all", "All Review-2 candidates ranked by macro-F1 (%, 100 fold-runs each)",
            ["Rank", "Model", "Kind", "Accuracy", "Bal. acc.", "Macro-F1"], rows,
            [720, 4608, 1440, 1008, 1008, 1008], align=["center", "left", "left", "center", "center", "center"], sz=18,
            bold_rows=(0,), keep_next=False)
    r.figure("f_top", F2 / "B_model_comparison.png", "The leading candidates on accuracy, balanced accuracy and macro-F1", 6.2)

    r.h2("Consistency Across Repeats", key="s_paired")
    rows = []
    for x in R.paired.itertuples():
        rows.append([R.nice_model(x.model), R.nice_model(x.compared_with), "macro-F1" if x.metric == "macro_f1" else "accuracy",
                     f"{x.mean_difference:+.2f}", f"{int(x.repeats_won)} / {int(x.repeats)}", f"{x.wilcoxon_p:.3f}"])
    r.para("Every candidate was scored on identical folds in each repeat, so their per-repeat scores can be paired (Table [[t_paired]]). "
           "Random Forest with SMOTE beats the Review-1 ensemble on macro-F1 in 10 of 10 repeats and loses on accuracy in 9 of 10; the "
           "learned-temperature ensemble beats the paper's ensemble on both metrics in all 10 repeats. The repeats reuse the same 1,599 wines "
           "with different splits, so they are not independent samples and the Wilcoxon signed-rank p-values {c:wilcoxon1945} are "
           "optimistic {c:nadeau2003}, {c:demsar2006}; the win counts are the plainer evidence.")
    r.table("t_paired", "Paired comparison over the 10 repeats",
            ["Model", "Compared with", "Metric", "Mean diff.", "Repeats won", "Wilcoxon p"], rows,
            [2448, 2448, 1152, 1152, 1152, 1152], align=["left", "left", "center", "center", "center", "center"], sz=18)

    r.h2("Feature Importance")
    im = R.imp.sort_values("rank_final")
    rows = []
    for x in im.itertuples():
        rows.append([str(int(x.rank_final)), x.feature, f2(x.final_f1_drop), f2(x.rf_f1_drop), f"{x.rf_mdi:.3f}", f"{x.spearman_rho:+.2f}",
                     "yes" if x.highlighted_by_paper else ""])
    r.para("Table [[t_imp]] gives the three importance measures of Section [[s_fimethods]] for the best model (Random Forest with SMOTE) "
           "and for the Review-1 Random Forest. Permutation importance is the macro-F1 lost, in points, when a feature is shuffled on the "
           "held-out folds. The three rankings agree closely (pairwise rank correlation "
           f"{R.agree.min():.2f}–{R.agree.max():.2f}): **alcohol, sulphates and volatile acidity** are clearly the most important, followed "
           "by chlorides and total sulphur dioxide. Three of the four attributes the paper highlights are in the top three; citric acid "
           "ranks sixth. Higher alcohol, sulphates and citric acid go with better wine, higher volatile acidity with worse (Figures "
           "[[f_perm]] and [[f_methods]]). Small negative values mean that shuffling a feature made no difference beyond noise; these "
           "features are partly redundant with others, such as density with alcohol.")
    r.table("t_imp", "Feature importance: permutation importance (macro-F1 points), MDI and Spearman correlation",
            ["Rank", "Feature", "Perm., best model", "Perm., RF", "MDI, RF", "Spearman ρ", "Paper's key attribute"], rows,
            [720, 2304, 1440, 1152, 1152, 1152, 1584], align=["center", "left", "center", "center", "center", "center", "center"], sz=19)
    r.figure("f_perm", F2 / "C1_permutation_importance.png", "Permutation importance on the held-out folds (macro-F1 lost when a feature is shuffled)", 6.2)
    r.figure("f_methods", F2 / "C2_importance_methods_and_direction.png", "The three importance measures side by side, with the direction of each effect", 6.4)
    rows = [[x.subset.replace(" (chosen in-fold)", ""), str(int(x.n_features)), f2(x.accuracy), f2(x.macro_f1), x.features_most_often_chosen]
            for x in R.subset.itertuples()]
    s4 = R.subset[R.subset["n_features"] == 4].iloc[0]
    r.para("How many laboratory tests are needed? Table [[t_subset]] and Figure [[f_subset]] retrain Random Forest on the top-k "
           f"features chosen inside each training fold. Four tests – alcohol, volatile acidity, sulphates and chlorides – already give "
           f"{f2(s4['accuracy'])} % accuracy, within {f2(a['RF'] - s4['accuracy'])} points of all eleven, and the best macro-F1 of the curve. "
           "A retailer could therefore screen wines with a few routine tests.")
    r.table("t_subset", "Random Forest on the top-k features chosen inside each training fold (%)",
            ["Subset", "Tests", "Accuracy", "Macro-F1", "Features chosen most often"], rows,
            [1872, 720, 1152, 1152, 4752], align=["left", "center", "center", "center", "left"], sz=18)
    r.figure("f_subset", F2 / "C3_feature_subset.png", "Accuracy and macro-F1 against the number of laboratory tests used", 5.8)

    r.h2("Reference Paper Result vs Our Result")
    h = R.headline
    paper_rec = dict(zip(R.CLASSES, R.C.MA_2024_PER_CLASS_PRECISION))
    rows = [["Accuracy (%)", "89.73", f2(h.loc["accuracy", "review1_ensemble"]), f2(h.loc["accuracy", "review1_random_forest"]), f2(h.loc["accuracy", "review2_best"])],
            ["Balanced accuracy (%)", f2(sum(paper_rec.values()) / 6), f2(h.loc["balanced_accuracy", "review1_ensemble"]),
             f2(h.loc["balanced_accuracy", "review1_random_forest"]), f2(h.loc["balanced_accuracy", "review2_best"])],
            ["Macro-F1 (%)", "not reported", f2(h.loc["macro_f1", "review1_ensemble"]), f2(h.loc["macro_f1", "review1_random_forest"]), f2(h.loc["macro_f1", "review2_best"])]]
    for c in R.CLASSES:
        rows.append([f"Recall, grade {c} (%)", f2(paper_rec[c]), f2(h.loc[f"recall_{c}", "review1_ensemble"]),
                     f2(h.loc[f"recall_{c}", "review1_random_forest"]), f2(h.loc[f"recall_{c}", "review2_best"])])
    r.para("Table [[t_final]] brings the results together. The balanced accuracy of the paper is computed here as the mean of its "
           "per-class values; the paper does not report macro-F1.")
    r.table("t_final", "Reference Paper Result vs Our Reproduction Result (Review 1) vs the best Review-2 model",
            ["Metric", "Reference Paper Result", "Review-1 ensemble", "Review-1 Random Forest", "Review-2 best (RF + SMOTE)"], rows,
            [2448, 1872, 1728, 1872, 1872], align=["left"] + ["center"] * 4, sz=19)

    r.h2("Discussion")
    r.para("Three findings stand out. First, the weighted ensemble of the base paper was implemented as specified, with leakage-free "
           f"evaluation, and reaches {f2(a['Ensemble (soft vote)'])} % – inside the range this dataset normally gives and within "
           f"{f2(R.cons['our_gap_vs_their_weighted_average_pct_points'])} points of what the paper's own weights and base accuracies imply. "
           "The 89.73 % could not be reconciled with the paper's own tables. The cause on our side is structural, not an implementation "
           "detail: normalising inverse errors and error distances of similar learners gives nearly equal weights, so the ensemble "
           "averages its members instead of exceeding the best of them – consistent with the observation of Kuncheva and Whitaker "
           "{c:kuncheva2003} that diversity does not translate simply into accuracy.")
    r.para("Second, class balancing does what it should. Accuracy rewards predicting grades 5 and 6; balancing gives up some of that to "
           f"recognise the rare grades, and the best model raises macro-F1 by {f2(h.loc['macro_f1', 'change_vs_review1_ensemble'])} points "
           f"and grade-4 recall by {f2(h.loc['recall_4', 'change_vs_review1_ensemble'])} points over the Review-1 ensemble. Grade 3 remains "
           "almost unpredictable with ten examples. Which model to deploy depends on the use: Random Forest for the most correct grades "
           "overall, Random Forest with SMOTE to find the unusual wines – both are offered in the web application.")
    r.para("Third, the Review-1 diagnosis held when tested: sharpening the weights lets the ensemble overtake Random Forest, and choosing "
           "the sharpness inside the training folds improves the paper's ensemble in every repeat. Three independent importance measures "
           "agree on what drives the prediction, and they confirm three of the paper's four key attributes. None of the configurations "
           f"approaches 89.73 %: the best accuracy of any honest configuration is {f2(a['RF'])} %, which strengthens the Review-1 conclusion.")


def chapter5(r):
    r.chapter("WEB APPLICATION: DESIGN AND DEPLOYMENT")
    r.h2("Purpose of the Web Application")
    r.para("The analysis lives in Python modules and result files, which is convenient for development but not for a reviewer or a "
           "wine buyer. The project therefore includes an interactive web application built with Streamlit {c:streamlit2026} and Altair "
           "charts {c:vanderplas2018}. It presents every result of the project and predicts the quality of new wines without any "
           f"programming. It is published at {APP} and its source code is available at {REPO}. Its goals are to:")
    r.bullets([
        "**explore** the dataset, the reproduction, the class-balancing experiment, the improvements and the feature importance with charts and tables;",
        "**predict** the quality grade of a wine from its 11 measurements with two models: the most accurate (Random Forest) and the best on the rare grades (Random Forest with SMOTE);",
        "**score in bulk:** upload a CSV file of wines and download their predicted grades; and",
        "**stay faithful to the project:** use exactly the project's models and numbers, which automated checks confirm.",
    ])

    r.h2("System Architecture")
    r.para("Figure [[f_apparch]] shows how the application is built. The result pages read the tables and figures written by "
           "run_all.py, so they always show the numbers of this report. For prediction, the application imports the project's own "
           "model definitions from src/ and trains the two models once at start-up on all 1,599 wines; Streamlit's resource cache keeps "
           "them in memory, so later visits are instant. The application is deployed from the GitHub repository to Streamlit Community "
           "Cloud, and app/test_app.py checks it automatically.")
    r.figure("f_apparch", FIG / "app_architecture.png", "Architecture of the web application", 6.4)

    r.h2("Technology Stack")
    r.para("Table [[t_stack]] lists the software. The library versions are pinned to exactly those with which the results were "
           "produced, so the application reproduces the project's models.")
    r.table("t_stack", "Technology stack of the project",
            ["Layer", "Technology", "Version", "Role in the project"],
            [["Language", "Python", "3.11", "models, experiments, figures and the web application"],
             ["Data handling", "pandas {c:mckinney2010}, NumPy {c:harris2020}", "3.0.5, 2.4.6", "loading the data, result tables"],
             ["Machine learning", "scikit-learn {c:pedregosa2011}, SciPy {c:virtanen2020}", "1.9.0, 1.17.1", "pipelines, learners, cross-validation, metrics, statistics"],
             ["Class balancing", "imbalanced-learn {c:lemaitre2017}", "0.14.2", "SMOTE inside the training folds"],
             ["Figures", "Matplotlib {c:hunter2007}", "3.11.1", "figures of the experiments and of this report"],
             ["Web framework", "Streamlit {c:streamlit2026}", "1.66.0", "pages, navigation, caching, widgets, file upload and download"],
             ["Interactive charts", "Altair {c:vanderplas2018}", "6.3.0", "bar charts of the predicted probabilities"],
             ["Version control", "Git and GitHub", "–", "public repository of the project"],
             ["Hosting", "Streamlit Community Cloud", "–", "free hosting; redeploys on every push"]],
            [1872, 2880, 1584, 3312], sz=19)

    r.h2("Pages and Features")
    r.para("The application has seven pages, listed in the sidebar (Table [[t_pages]]).")
    r.table("t_pages", "Pages of the web application",
            ["Page", "What it shows", "What the user can do"],
            [["Overview", "the project in brief: dataset, headline numbers of Review 1 and Review 2, a guide to the pages", "navigate to every page"],
             ["Dataset", "the class distribution, summary statistics and the correlation of each measurement with quality", "inspect the data"],
             ["Review 1: reproduction", "model ranking, per-class comparison with the published benchmarks and the two checks of Section 4.4", "compare the reproduction with the paper"],
             ["Review 2: class balancing", "accuracy, macro-F1 and per-class recall under the four balancing schemes", "see the effect of balancing"],
             ["Review 2: improving the result", "the temperature test, the learned temperature, the paired comparison and all candidates", "compare every candidate model"],
             ["Feature importance", "the three importance measures, their agreement and the top-k laboratory-test curve", "see what drives the prediction"],
             ["Predict a wine", "the grade predicted by both models with the probability of every grade; batch prediction", "set 11 sliders or start from a typical wine; upload a CSV file"]],
            [2304, 4320, 3024], sz=19)

    r.h2("Worked Examples")
    ex = __import__("pandas").read_csv(R.DATA / "app_examples.csv")
    rows = [[x.example, f"{x.alcohol:.2f}", f"{x._3:.2f}", f"{x.sulphates:.2f}", f"{x.rf_grade} ({x.rf_prob:.1f} %)", f"{x.smote_grade} ({x.smote_prob:.1f} %)"]
            for x in ex.itertuples()]
    e = ex.set_index("example")
    rf, sm = e["rf_grade"], e["smote_grade"]
    assert (rf["Typical grade-5 wine"], rf["Typical grade-6 wine"], rf["Typical grade-7 wine"]) == (5, 6, 7)
    assert (sm["Typical grade-5 wine"], sm["Typical grade-6 wine"]) == (5, 6)
    assert rf["Typical grade-4 wine"] == sm["Typical grade-4 wine"] == 5
    assert (rf["Typical grade-8 wine"], sm["Typical grade-8 wine"], sm["Typical grade-7 wine"]) == (7, 8, 8)
    r.para("The prediction page can start from the median measurements of all wines or of the wines of one grade. Table [[t_examples]] "
           "shows what the two models predict for these typical wines. Both models recover the grade of the typical grade-5 and grade-6 "
           "wines, and Random Forest also that of the grade-7 wine. For the typical grade-4 wine both predict 5 – the boundary that the "
           "rare grades fall across. For the typical grade-8 wine Random Forest predicts 7, while the SMOTE model predicts 8 with "
           f"{e.loc['Typical grade-8 wine', 'smote_prob']:.0f} % probability – but it also predicts 8 for the typical grade-7 wine. This "
           "is the trade-off of Chapter 4 in miniature: the SMOTE model finds the rare grades more often at the price of some errors on "
           "the common ones.")
    r.table("t_examples", "Example wines in the web application: three key measurements and the predicted grade (probability)",
            ["Example (median of)", "Alcohol (% vol.)", "Volatile acidity", "Sulphates", "Random Forest", "RF + SMOTE"], rows,
            [2880, 1296, 1296, 1152, 1512, 1512], align=["left"] + ["center"] * 5, sz=19)
    r.para("The batch tab accepts a CSV file with the 11 measurement columns, separated by commas or semicolons, reports any missing "
           "column by name and returns the input with both predictions added. A sample file can be downloaded from the page.")

    r.h2("Verification of the Application")
    r.para("The file app/test_app.py contains 15 automated checks in four groups (Table [[t_tests]]); all 15 pass (Figure [[f_outtests]]).")
    r.table("t_tests", "Automated checks of the web application",
            ["Group", "Checks", "What is verified"],
            [["1. Pages", "7", "every page renders without an exception"],
             ["2. Models", "2", "the two models give exactly the predictions of freshly fitted project models (Review-1 Random Forest; Review-2 SMOTE Random Forest), which proves identical settings"],
             ["3. Predictions", "4", "probabilities sum to 1 and every predicted grade is a real grade, for both models"],
             ["4. Numbers", "2", "the reproduction accuracy shown is 69.01 % and the best macro-F1 model is RF + SMOTE, as in the result files"]],
            [1872, 1152, 6624], align=["left", "center", "left"])

    r.h2("Deployment")
    r.para("The project is version-controlled in a public GitHub repository (Table [[t_repo]]) and the application is hosted on Streamlit "
           "Community Cloud, which installs the pinned app/requirements.txt with Python 3.11 and redeploys after every push. The base paper's "
           "PDF is excluded from the repository by .gitignore because it is a copyrighted article. The application can also be run locally "
           "with the command streamlit run app/streamlit_app.py. On the free tier the application sleeps after a period without visitors "
           "and wakes up in about a minute.")
    r.table("t_repo", "Structure of the GitHub repository",
            ["Path", "Contents"],
            [["app/", "streamlit_app.py (the seven pages), test_app.py (15 checks), requirements.txt"],
             ["src/", "config.py, preprocessing.py, base_learners.py, ensemble.py, evaluate.py (Review 1); review2.py, feature_importance.py (Review 2)"],
             ["run_all.py", "runs every experiment: python run_all.py (Review 1), python run_all.py --review2 (Review 2)"],
             ["data/raw/", "the UCI red- and white-wine files"],
             ["results/", "tables/ and figures/ of Review 1; review2/tables and review2/figures of Review 2"],
             ["notebooks/", "a Google Colab notebook that runs the whole project"],
             ["report/", "methodology.md, the report's figures and the scripts that build this report and the conference paper"],
             ["README.md, HOW_TO_RUN.md, DEPLOY.md", "overview, running instructions and deployment steps"]],
            [2880, 6768], sz=19)

    r.h2("Snapshots of the Web Application")
    shots = [
        ("app_overview", "Overview page: the project in brief and the headline numbers"),
        ("app_dataset", "Dataset page: class distribution, summary statistics and correlations"),
        ("app_reproduction", "Review 1 page: model ranking and comparison with the published benchmarks"),
        ("app_class_balancing", "Review 2 page: class balancing"),
        ("app_improvement", "Review 2 page: improving the result"),
        ("app_feature_importance", "Feature importance page"),
        ("app_predict", "Predict page: grades and probabilities from both models, and batch prediction"),
    ]
    parts = FIG / "app" / "parts"
    for stem, cap in shots:
        files = sorted(parts.glob(f"{stem}_*of*.png"))
        for k, f in enumerate(files):
            suffix = f" (part {k + 1} of {len(files)})" if len(files) > 1 else ""
            from PIL import Image
            w, h = Image.open(f).size
            width = min(6.4, 8.6 * w / h)
            r.figure(f"f_{stem}_{k + 1}", f, cap + suffix, width)


def _source(path, name):
    """Lines of a function/class from the project's source, without docstring and comment-only lines."""
    lines = (ROOT / path).read_text().splitlines()
    i = next(k for k, line in enumerate(lines) if re.match(rf"\s*(def|class) {name}\b", line))
    indent = len(lines[i]) - len(lines[i].lstrip())
    out = [lines[i]]
    k = i + 1
    while k < len(lines):
        line = lines[k]
        if line.strip() and len(line) - len(line.lstrip()) <= indent and not line.lstrip().startswith((")", "]", "}")):
            break
        out.append(line)
        k += 1
    body, in_doc = [], False
    for k, line in enumerate(out):
        s = line.strip()
        if k > 0 and (s.startswith('"""') or in_doc):
            if s.startswith('"""') and (s.count('"""') == 2 and len(s) > 3):
                continue
            in_doc = not in_doc if s.count('"""') == 1 else in_doc
            continue
        if s.startswith("#"):
            continue
        body.append(line[indent:])
    while body and not body[-1].strip():
        body.pop()
    return body


def _lines(path, names):
    out = []
    for line in (ROOT / path).read_text().splitlines():
        if any(line.startswith(n) for n in names):
            out.append(line.split("  #")[0].rstrip())
    return out


def chapter6(r):
    r.chapter("SOURCE CODE AND SNAPSHOTS")
    r.para(f"The complete source code is in the project repository ({REPO}). The excerpts below are taken directly from the project's "
           "files and show the core of each step; docstrings and comments are left out.")
    r.h2("Settings")
    r.code(_lines("src/config.py", ["RANDOM_STATE", "N_SPLITS", "N_REPEATS", "BENCHMARK_CLASSES", "MA_2024_OVERALL_ACCURACY",
                                    "REVIEW2_PRIMARY_METRIC", "SMOTE_K_NEIGHBORS", "WEIGHT_TEMPERATURES", "FEATURE_SUBSET_SIZES",
                                    "PERMUTATION_REPEATS"]))
    r.h2("Data Loading and Scaling")
    r.code(_source("src/preprocessing.py", "load_red_wine") + [""] + _source("src/preprocessing.py", "get_features_target")
           + [""] + _source("src/base_learners.py", "_pipe"))
    r.h2("Base Learners")
    r.code(_source("src/base_learners.py", "get_base_learners"))
    r.h2("Ensemble Weights and Weighted Vote")
    r.code(_source("src/ensemble.py", "_error_vector") + [""] + _source("src/ensemble.py", "compute_weights") + [""]
           + _source("src/ensemble.py", "weighted_soft_vote"))
    r.h2("Repeated Cross-Validation")
    src = _source("src/ensemble.py", "run_repeated_cv")
    end = next(k for k, line in enumerate(src) if "per_repeat.append" in line)
    r.code(src[:end] + ["        ...  # per-repeat records are stored, then all repeats are pooled"])
    r.h2("Class Balancing")
    r.code(_source("src/review2.py", "BalancedSampleWeight") + [""] + _source("src/review2.py", "make_paper_learners"))
    r.h2("Learned Temperature")
    r.code(_source("src/review2.py", "tempered_weights") + [""] + _source("src/review2.py", "PaperWeightedEnsemble")[:40])
    r.h2("Feature Importance")
    r.code(_source("src/feature_importance.py", "_one_fold"))
    r.h2("Web Application")
    r.code(_source("app/streamlit_app.py", "trained_models") + [""] + _source("app/streamlit_app.py", "page_predict")[:34])
    r.h2("Output Snapshots")
    r.para("The following snapshots show real outputs of the project: the automated checks of the web application and the headline "
           "comparison of Review 1 and Review 2 read from the result files. The figures of Chapters 2 to 4 are the graphical outputs of "
           "the experiments, and the web application is shown in Section 5.8.")
    from PIL import Image
    for key, name, cap in [("f_outtests", "out_tests.png", "Output of the automated checks of the web application"),
                           ("f_outhead", "out_headline.png", "Output: headline metrics of Review 1 and the best Review-2 model")]:
        width = min(6.4, 0.8 * Image.open(FIG / name).size[0] / 200)   # terminal text at about 7.5 pt
        r.figure(key, FIG / name, cap, width)


def chapter7(r):
    r.chapter("MERITS AND DEMERITS")
    r.h2("Merits")
    r.numbered([
        "**Faithful and leakage-free:** the paper's weighting equations are implemented as written, and every scaler, resampler, "
        "selector and setting is fitted inside the training folds of a 10 × 10 cross-validation.",
        "**Checked against the paper's own numbers:** the gap to the published accuracy is explained with checks computed from the "
        "paper's tables, reported as figures that could not be reconciled rather than as accusations.",
        "**Honest about trade-offs:** macro-F1 was fixed as the Review-2 metric before the experiments, accuracy is always reported "
        "beside it, and both the most accurate and the most balanced model are offered.",
        "**Robust conclusions:** the main comparisons are confirmed repeat by repeat, and three different importance measures agree.",
        "**Reproducible and usable:** one command reruns every experiment, the numbers in the report are read from the result files, "
        "and a tested web application serves the models.",
    ])
    r.h2("Demerits")
    r.numbered([
        "**Two learners are substitutes:** Gradient Boosting and the MLP replace the RNN and the ELM, so the reproduction is not exact "
        "for those two members.",
        "**Rare grades remain hard:** with 10 wines of grade 3 and 18 of grade 8, even the best model recognises few of them, and the "
        "estimates for those grades are uncertain.",
        "**Only red wine:** the white-wine data of the same source are not used, so the findings are not tested on a second dataset.",
        "**Optimistic statistics:** the best model is chosen on the same cross-validation that scores it, and the repeats are not "
        "independent, so the paired p-values are indicative only.",
        "**Physicochemical inputs only:** price, region, vintage and taster information are not available, which limits any "
        "predictor of a sensory grade.",
    ])


def chapter8(r):
    r.chapter("CONCLUSION AND FUTURE PLANS")
    a = R.acc
    h = R.headline
    r.para("This project reproduced the accuracy- and diversity-weighted ensemble of Ma et al. for predicting the quality of red wine "
           "from its physicochemical measurements, and extended it with class balancing, an improved ensemble and a study of feature "
           f"importance. Evaluated with stratified 10-fold cross-validation repeated 10 times and without leakage, the reproduced ensemble "
           f"reaches {f2(a['Ensemble (soft vote)'])} % accuracy against the published 89.73 %, and Random Forest alone {f2(a['RF'])} %. "
           "The gap is explained by the paper's own tables: its weights are close to uniform, its base accuracies imply an ensemble near "
           f"{f2(R.cons['weighted_average_of_base_accuracies_pct'])} %, and its confusion matrix implies a "
           f"{int(R.t9['implied_test_set_size'])}-wine hold-out with {f2(R.t9['implied_overall_accuracy_pct'])} % accuracy.")
    r.para("The second review's requests were completed. Class balancing with SMOTE inside the training folds raised macro-F1 from "
           f"{f2(h.loc['macro_f1', 'review1_ensemble'])} to {f2(h.loc['macro_f1', 'review2_best'])} and grade-4 recall from "
           f"{f2(h.loc['recall_4', 'review1_ensemble'])} % to {f2(h.loc['recall_4', 'review2_best'])} %, at a stated cost of "
           f"{f2(-h.loc['accuracy', 'change_vs_review1_ensemble'])} accuracy points. Learning the sharpness of the weights inside each "
           f"training fold improved the paper's ensemble to {f2(g(R.LT_R1, 'accuracy'))} % in every repeat. Alcohol, sulphates and "
           "volatile acidity drive the prediction, and four routine tests give nearly all of the accuracy. The results are delivered "
           "through a tested web application.")
    r.label("Future Work:")
    r.numbered([
        "Repeat the study on the white-wine data and on both colours together.",
        "Treat quality as an ordered target (ordinal regression), so that predicting 6 for a grade-7 wine costs less than predicting 4.",
        "Use a nested cross-validation to select the final model and a corrected resampled t-test for confidence intervals.",
        "Try cost-sensitive thresholds that let a retailer choose how many unusual wines to flag.",
        "Extend the web application with explanations of individual predictions.",
    ])
