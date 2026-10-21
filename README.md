# Wine Quality Prediction Using Ensemble Learning

**A reproduction of Ma et al. (2024), *Journal of Business Research***

| | |
|---|---|
| **Author** | SURIANANDHAN S |
| **Register number** | 127018060 |
| **Course** | CSE425 — Machine Learning Essentials |
| **Guide** | Dr. Vidivelli S, AP-II |
| **Department** | CSE, School of Computing |

> Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to table:
> Uncovering wine quality for sales management through machine learning. *Journal of
> Business Research*, 176, 114576. https://doi.org/10.1016/j.jbusres.2024.114576

Dataset: [UCI Machine Learning Repository — Wine Quality (Red)](https://archive.ics.uci.edu/dataset/186/wine+quality)
· [direct CSV](https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv)

---

## 1. What this is

A B.Tech CSE425 mini-project (classical ML only — no deep learning beyond a standard
backprop MLP) that reproduces the weighted-ensemble wine-quality framework of Ma et al.
(2024) on the 1,599-sample UCI red wine dataset.

**Headline result:** the reproduction reaches **69.01%** overall accuracy against the
paper's reported **89.73%**, and our ensemble does not overtake its strongest base
learner. Rather than leave that as an unexplained shortfall, the project derives — from
the paper's own published tables — why the two numbers differ. That analysis is the main
contribution and is written up in [`report/methodology.md`](report/methodology.md) §4.3.

## 2. Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
```

| Command | What it does | Runtime |
|---|---|---|
| `python run_all.py` | Full protocol: 10-fold CV × 10 repeats (100 fold-runs) | ~2 min |
| `python run_all.py --quick` | Fast sanity pass: 10-fold CV × 2 repeats | 29 s |
| `python run_all.py --review2` | Also runs Review 2 (balancing, improvements, feature importance) | see §6 |
| `python run_all.py --with-novelty` | Also runs the optional unsupervised extension | +~1 min |

Tables are written to `results/tables/`, figures to `results/figures/`. `--quick` runs a
reduced protocol, so it writes to a separate git-ignored `results/_quick_run/` and cannot
overwrite the canonical 10-repeat numbers this README quotes.

Use the virtual environment. Without it you get whatever Python is first on `PATH`, which
on the development machine is an Anaconda install with older package versions and no
`mlxtend` (so `--with-novelty` fails). [`HOW_TO_RUN.md`](HOW_TO_RUN.md) has the full
walkthrough, including where each number on the review slides comes from.
[`notebooks/reproduction_walkthrough.ipynb`](notebooks/reproduction_walkthrough.ipynb)
walks through the same pipeline cell by cell.

Individual modules are also runnable standalone for inspection:

```bash
cd src && python preprocessing.py
```

## 3. Project structure

```
wine-quality-ml-project/
├── data/raw/                     winequality-red.csv (used), winequality-white.csv
├── paper/                        base paper PDF (local only -- copyrighted, see DOI above)
├── src/
│   ├── config.py                 paths, protocol settings, published benchmark constants
│   ├── preprocessing.py          data loading; raw-X loader for CV
│   ├── base_learners.py          SVM, RF, MLP, GradientBoosting — each in a scaling Pipeline
│   ├── ensemble.py               Eqs. (1)-(9); soft + hard weighted voting; 10x10 CV
│   ├── evaluate.py               confusion matrices, per-class metrics, paper reconciliation
│   ├── review2.py                Review 2: class balancing, weight sharpening, stacking
│   ├── feature_importance.py     Review 2: permutation importance, lab-test subsets
│   └── novelty_cluster_mine_feedback.py    optional extension (opt-in only)
├── notebooks/
│   ├── reproduction_walkthrough.ipynb
│   ├── wine_quality_colab.ipynb  self-contained Google Colab version (generated)
│   └── build_colab_notebook.py   regenerates the Colab notebook from src/
├── results/
│   ├── tables/, figures/         Review 1 (the reproduction) -- the baseline
│   └── review2/                  Review 2 tables, figures and run log
├── app/                          Streamlit web app, its 15 checks, requirements.txt
├── report/                       methodology.md, figures, and the scripts that build the report and paper
├── HOW_TO_RUN.md                 step-by-step run guide
├── DEPLOY.md                     putting the web app online
├── run_all.py
└── requirements.txt
```

## 4. What was substituted, and why

The paper's ensemble is **SVM + RNN + ELM + Random Forest**. Two of those fall outside a
classical-ML-only syllabus:

- **RNN → `GradientBoostingClassifier`.** An RNN is a deep-learning sequence model
  requiring backprop-through-time. Gradient boosting fits each new tree to the residual
  errors of the trees before it — the closest in-syllabus analogue to iterative
  refinement. (The brief permits AdaBoost or Gradient Boosting; AdaBoost's default
  depth-1 stumps scored around 49% in an early exploratory run, so we use GB. That run
  predates the current pipeline and is not recorded in `results/`, so treat the figure as
  an informal observation rather than a reported result.)
- **ELM → `MLPClassifier`.** An ELM uses random *fixed* hidden weights with a closed-form
  output layer — explicitly not backpropagation. An MLP is the closest analogue that is
  still a neural network but is trained end-to-end by standard backprop.
- **SVM and Random Forest are unchanged** — both are already classical ML.

## 5. Results

### 5.1 Model ranking (10-fold CV × 10 repeats)

| Rank | Model | Overall accuracy |
|---|---|---|
| 1 | Random Forest | **71.03%** |
| 2 | Ensemble (hard vote) | 69.93% |
| 3 | Ensemble (soft vote) | 69.01% |
| 4 | GradientBoosting *(substitutes RNN)* | 67.67% |
| 5 | SVM | 61.95% |
| 6 | MLP *(substitutes ELM)* | 61.35% |

The paper's central claim — ensemble beats every base learner, by 9.02 points — **does
not reproduce**. Ours lands 2.02 points below Random Forest. §5.3 explains why.

### 5.2 Per-class comparison

Values use the paper's own metric definition, which is per-class **recall** (see below).

| Class | n | Cortez et al. (2009) | Ma et al. (2024) | Ours |
|---|---|---|---|---|
| 3 | 10 | 0.00% | 33.33% | 0.00% |
| 4 | 53 | 20.00% | 63.16% | 0.57% |
| 5 | 681 | 67.50% | 84.80% | **81.66%** |
| 6 | 638 | 57.70% | 88.06% | **69.87%** |
| 7 | 199 | 58.60% | 77.08% | 49.90% |
| 8 | 18 | 0.00% | 50.00% | 11.11% |
| **Overall** | 1599 | — | **89.73%** | **69.01%** |

> **Terminology:** Ma et al. call this metric "precision", but their own worked example
> (Eq. 14) divides by the *actual class total* — that is recall. Our check confirms it:
> 4 of their 6 published values reproduce column-wise (3 of them exactly; class 6 only to
> within 0.6 points), against just 1 of 6 row-wise. We report
> their metric under their definition for like-for-like comparison, and give conventional
> precision/recall/specificity separately in `results/tables/metrics_*.csv`.

### 5.3 Why 89.73% does not reproduce

Two checks, both computed in code from the paper's own printed numbers:

**(a) Their Table 9 confusion matrix.** Its cells sum to **491 samples** — 30.7% of the
dataset, i.e. a single hold-out split, not the 100-run cross-validation the text
describes. Its own diagonal gives **403/491 = 82.08%**, which is 7.65 points below the
89.73% stated in the text.

**(b) Their Table 8 weights × their Tables 4-7 accuracies.** The paper's final weights
(0.2516 / 0.2286 / 0.2168 / 0.3030) are never more than 0.053 from a uniform 0.25.
Applied to their own base accuracies they give **67.52%**:

| | Accuracy |
|---|---|
| Weighted average implied by the paper's own numbers | 67.52% |
| **Our reproduction** | **69.01%** — within **1.49 points** |
| Paper's reported ensemble | 89.73% — **22.21 points** above |

This also explains our own ranking. Our measured weights span just 0.2356–0.2698 (max
deviation 0.0198 from uniform), because Eqs. (5) and (9) don't discriminate sharply
between learners with similar error rates. With weights that flat, the ensemble
approximates an unweighted average of its members — which lands *between* the strongest
and weakest, not above the strongest.

*Caveat:* Table 9 was transcribed by eye from the printed PDF and may contain reading
errors (two of six per-class values don't match, most likely for that reason). This is
reported as "could not reconcile", **not** as a claim that the paper is wrong.

*Context:* published accuracy for this 6-class task typically falls in the 62–72% range.
Ours sits inside it; 89.73% sits above it.

### 5.4 Methodological notes

- **No data leakage.** Min-max scaling runs inside each learner's `Pipeline`, fit on the
  training fold only. Scaling the full dataset before CV — as an earlier version did —
  leaks test-fold statistics.
- **Class imbalance.** Classes 3 and 8 have 10 and 18 samples. SVM and RF use balanced
  class weights; the paper states no imbalance handling, so this is our own choice.
- **Both readings of Eq. (1)** — soft vote (weighted sum of probability vectors) and hard
  vote (weighted majority) — are implemented and reported, since the paper is ambiguous.

<!-- REVIEW2-SECTION:BEGIN -->
<!-- Generated by presentation/build_review2_docs.py from results/review2/tables -- do not edit by hand. -->

## 6. Review 2 — class balancing, improving the result, feature importance

At Review 1 the guide asked for three changes: class balancing, an improved result, and
feature importance. All three are in [`src/review2.py`](src/review2.py) and
[`src/feature_importance.py`](src/feature_importance.py):

```bash
python run_all.py --review2
```

Output goes to `results/review2/`; the Review-1 numbers in `results/tables/` stay exactly
as they were. Expect roughly 1½ hours on an 8-core laptop. 

**Primary metric: macro-F1**, fixed in `config.py` before any Review-2 run (accuracy rewards
predicting the two majority classes, which is exactly what balancing trades away). Accuracy
is reported alongside everywhere.

| Metric (%) | Review-1 ensemble | Review-1 Random Forest | Review-2 best | Change vs Review-1 ensemble |
|---|---|---|---|---|
| Accuracy | 69.01 | 71.03 | 67.94 | -1.08 |
| Balanced accuracy | 35.52 | 36.40 | 42.07 | +6.55 |
| **Macro-F1 (primary)** | 36.92 | 38.09 | 40.92 | +4.00 |
| Recall, class 3 | 0.00 | 0.00 | 4.00 | +4.00 |
| Recall, class 4 | 0.57 | 0.00 | 21.89 | +21.32 |
| Recall, class 5 | 81.66 | 81.97 | 78.00 | -3.66 |
| Recall, class 6 | 69.87 | 74.29 | 64.19 | -5.69 |
| Recall, class 7 | 49.90 | 51.06 | 65.43 | +15.53 |
| Recall, class 8 | 11.11 | 11.11 | 18.89 | +7.78 |

Best on macro-F1: **RF · SMOTE**. Best on accuracy: **RF · Review-1 setup**
(71.03%).

- **Class balancing.** SMOTE oversampling gives the paper's ensemble its best macro-F1
  (36.92 → 39.34); class-4 recall rises from 0.6% to
  26.4% with SMOTE, at a cost of 5.15 points of accuracy.
- **The Review-1 diagnosis, tested and fixed.** Sharpening the paper's weights overtakes Random Forest from T = 25.
  Choosing the sharpening inside each training fold (nested CV) takes the paper's own ensemble
  from 69.01% to 70.89%, winning 10 of 10 repeats.
- **Feature importance.** Alcohol, sulphates and volatile acidity drive the prediction; three importance
  methods agree (rank correlation 0.74–0.89). Four lab tests reach 69.27%
  accuracy against 71.03% with all eleven.
- **Still nowhere near 89.73%** — consistent with the Review-1 finding.

Full write-up: [`report/methodology.md`](report/methodology.md) §6. Slides:
[`presentation/second_review.pptx`](presentation/second_review.pptx).

<!-- REVIEW2-SECTION:END -->

## 7. Optional extension

`python run_all.py --with-novelty` additionally runs K-means/Ward clustering, Isolation
Forest and LOF outlier detection, a cluster-ID feedback feature, and FP-Growth
association rule mining. This is coursework beyond the reproduction; see the appendix of
[`report/methodology.md`](report/methodology.md). Notable: the cluster-feedback feature
produced **no improvement on the three classes it targeted** (3, 4 and 8 all changed by
exactly 0.00; classes 5 and 6 declined, class 7 rose 0.50) — a negative result, reported
as such.

## 8. Links

- Dataset: https://archive.ics.uci.edu/dataset/186/wine+quality
- Base paper DOI: https://doi.org/10.1016/j.jbusres.2024.114576
