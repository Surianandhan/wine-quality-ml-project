/**
 * build_deck.js — generates first_review.pptx
 *
 * Every number in this deck is copied from results/tables/*.csv. Nothing is
 * invented. If the pipeline is re-run and numbers change, update them here.
 *
 *   node build_deck.js
 */
const pptxgen = require("pptxgenjs");
const path = require("path");

const FIG = path.join(__dirname, "..", "results", "figures", "accuracy_comparison.png");

// ---- palette: wine-appropriate berry / rose / gold ------------------------
const BERRY = "6D2E46";
const ROSE = "A26769";
const GOLD = "C8A45C";
const INK = "2B2B2B";
const MUTED = "6E6E6E";
const TINT = "F5EFF1";
const WHITE = "FFFFFF";

const HEAD = "Cambria";
const BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "SURIANANDHAN S";
pres.title = "Wine Quality Prediction Using a Weighted Ensemble";

// ---- helpers --------------------------------------------------------------
function title(slide, text, sub) {
  slide.addText(text, {
    x: 0.6, y: 0.35, w: 12.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: BERRY,
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.6, y: 1.03, w: 12.1, h: 0.35, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, color: MUTED, italic: true,
    });
  }
}

const SLIDE_H = 7.5;
const SAFE_BOTTOM = 7.2; // keep every box inside a 0.3" bottom gutter

function bullets(slide, items, opts) {
  const o = Object.assign({ x: 0.6, y: 1.6, w: 7.2, h: 4.6, fontSize: 15 }, opts || {});
  // Never let the box run off the bottom of the slide.
  const h = Math.min(o.h, SAFE_BOTTOM - o.y);
  slide.addText(
    items.map((t, i) => ({
      text: t,
      options: { bullet: true, breakLine: i !== items.length - 1 },
    })),
    {
      x: o.x, y: o.y, w: o.w, h, isTextBox: true, margin: 0,
      valign: "top", // else the text centres in the box and leaves a gap above
      fontFace: BODY, fontSize: o.fontSize, color: INK,
      paraSpaceAfter: 10, lineSpacing: 22,
    }
  );
}

function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill || TINT }, line: { color: fill || TINT, width: 0 },
  });
}

function statCard(slide, x, y, w, value, label, valColor, fill) {
  card(slide, x, y, w, 1.5, fill || TINT);
  slide.addText(value, {
    x: x, y: y + 0.18, w: w, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: valColor || BERRY, align: "center",
  });
  slide.addText(label, {
    x: x + 0.15, y: y + 0.95, w: w - 0.3, h: 0.45, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: MUTED, align: "center",
  });
}

function numCircle(slide, x, y, n) {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.42, h: 0.42,
    fill: { color: BERRY }, line: { color: BERRY, width: 0 },
  });
  slide.addText(String(n), {
    x, y: y + 0.03, w: 0.42, h: 0.36, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: WHITE, align: "center",
  });
}

function tableOn(slide, rows, opts) {
  const o = Object.assign({ x: 0.6, y: 1.7, w: 12.1, fontSize: 13 }, opts || {});
  slide.addTable(rows, {
    x: o.x, y: o.y, w: o.w, colW: o.colW,
    fontFace: BODY, fontSize: o.fontSize, color: INK,
    border: { type: "solid", color: "E3D8DC", pt: 1 },
    align: "left", valign: "middle",
    autoPage: false,
  });
}

function hrow(cells) {
  return cells.map((c) => ({
    text: c,
    options: { bold: true, color: WHITE, fill: { color: BERRY }, fontSize: 12 },
  }));
}

// =========================================================================
// 1 — TITLE
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Wine Quality Prediction\nUsing a Weighted Ensemble", {
    x: 0.9, y: 1.25, w: 11.5, h: 1.8, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, lineSpacing: 46,
  });
  s.addText("A reproduction study of Ma et al. (2024), Journal of Business Research 176:114576", {
    x: 0.9, y: 3.1, w: 11.5, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15, color: GOLD, italic: true,
  });
  s.addText(
    [
      { text: "SURIANANDHAN S", options: { bold: true, fontSize: 19, breakLine: true } },
      { text: "127018060", options: { fontSize: 15, color: "E8DCE1", breakLine: true } },
      { text: "CSE425 — Machine Learning Essentials", options: { fontSize: 14, color: "E8DCE1" } },
    ],
    { x: 0.9, y: 4.0, w: 6.0, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE }
  );
  s.addText(
    [
      { text: "Guide", options: { fontSize: 11, color: GOLD, breakLine: true } },
      { text: "Dr. Vidivelli S, AP-II", options: { bold: true, fontSize: 15, breakLine: true } },
      { text: "Department of CSE, School of Computing", options: { fontSize: 13, color: "E8DCE1" } },
    ],
    { x: 7.2, y: 4.0, w: 5.2, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE }
  );
  s.addText("First Review", {
    x: 0.9, y: 6.35, w: 5, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: GOLD,
  });
  s.addNotes(
    "Good morning. My project is a reproduction study of a 2024 Journal of Business Research paper " +
    "on predicting wine quality from laboratory measurements using an ensemble of machine learning models. " +
    "I re-implemented their method under our classical machine learning syllabus and compared what it " +
    "actually produces against what they report."
  );
}

// =========================================================================
// 2 — ABSTRACT  (FRAMING PLANT)
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The project in 30 seconds", "Task, result, and contribution — stated up front");

  statCard(s, 0.6, 1.65, 3.4, "89.73%", "REPORTED BY THE PAPER", ROSE);
  statCard(s, 4.3, 1.65, 3.4, "69.01%", "OUR FAITHFUL REPRODUCTION", BERRY);
  statCard(s, 8.0, 1.65, 4.7, "3 checks", "EXPLAIN THE GAP, FROM THE PAPER'S OWN TABLES", BERRY);

  bullets(s, [
    "Task: predict a wine's 3–8 sensory quality score from 11 physicochemical lab measurements (1,599 red wines, UCI)",
    "Base paper: a weighted ensemble of four learners, reporting 89.73% overall accuracy",
    "This work: the same method, implemented faithfully, reaches 69.01%",
    "The project IS that gap — it is an investigation, not an attempt to tune the number upward",
    "Contribution: a leak-free reproduction, a three-check diagnosis, and a terminology correction in the paper's own metric",
  ], { y: 3.45, w: 12.1, fontSize: 14.5 });

  s.addNotes(
    "Here is the whole project on one slide, including the result, so nothing is a surprise later. " +
    "The paper reports 89.73 percent. My implementation of the same method reaches 69.01 percent. " +
    "The project is not an attempt to close that gap by tuning — it is an investigation into where the " +
    "gap comes from, and I resolve it using three independent checks computed from the paper's own tables. " +
    "[DELIVERY: slow down here. This is the most important 20 seconds of the presentation.]"
  );
}

// =========================================================================
// 3 — PROBLEM
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Problem statement", "Why predict a taste score from chemistry?");

  card(s, 0.6, 1.7, 5.9, 2.0);
  s.addText("The expensive signal", {
    x: 0.9, y: 1.9, w: 5.3, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 17, bold: true, color: BERRY,
  });
  s.addText("Quality is scored 3–8 by a three-sommelier sensory panel — slow, costly, and subjective.", {
    x: 0.9, y: 2.3, w: 5.3, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, color: INK, lineSpacing: 20,
  });

  card(s, 6.8, 1.7, 5.9, 2.0);
  s.addText("The cheap signal", {
    x: 7.1, y: 1.9, w: 5.3, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 17, bold: true, color: BERRY,
  });
  s.addText("11 physicochemical tests the winery already runs — alcohol, volatile acidity, sulphates, pH, density.", {
    x: 7.1, y: 2.3, w: 5.3, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, color: INK, lineSpacing: 20,
  });

  bullets(s, [
    "Business relevance: that quality score drives pricing, shelf placement and inventory decisions",
    "The ML question: can the objective measurements predict the subjective verdict?",
    "Why it is hard: six classes, severely imbalanced — 1,319 of 1,599 samples sit in just two of them",
  ], { y: 4.0, w: 12.1, fontSize: 15 });

  s.addNotes(
    "The score that decides a wine's price is assigned by a human tasting panel, which is slow and expensive. " +
    "The chemical tests are cheap and objective. So the question is whether the cheap measurements can predict " +
    "the expensive judgement. The difficulty is that almost the entire dataset sits in two of the six quality " +
    "levels, so the rare grades are very hard to learn."
  );
}

// =========================================================================
// 4 — LITERATURE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Literature survey", "Where this work sits");

  tableOn(s, [
    hrow(["Work", "Method", "Reported result"]),
    ["Cortez et al. (2009)", "SVM on the same 1,599 samples", "Per-class: 0 / 20.0 / 67.5 / 57.7 / 58.6 / 0"],
    [
      { text: "Ma et al. (2024) — base paper", options: { bold: true } },
      { text: "Weighted ensemble: SVM + RNN + ELM + RF", options: { bold: true } },
      { text: "89.73% overall, +9.02 over best base learner (RF 80.71%)", options: { bold: true } },
    ],
    ["This work", "Same ensemble, classical-ML substitutions", "69.01% + a diagnosis of the gap"],
  ], { y: 1.75, colW: [3.0, 4.3, 4.8] });

  bullets(s, [
    "Ma et al.'s novelty: weights combine an accuracy term AND a diversity term, not accuracy alone",
    "Published accuracy for this exact 6-class task is typically reported in the 62–72% range",
    "89.73% sits above that band — which is part of why this paper was worth reproducing",
  ], { y: 4.3, w: 12.1, fontSize: 15 });

  s.addNotes(
    "Cortez and colleagues introduced this dataset in 2009 and their per-class results are the standard baseline. " +
    "Ma and colleagues in 2024 built a weighted ensemble on top of it and reported 89.73 percent, which is a very " +
    "high figure for this task. The commonly reported range for this exact six-class problem is roughly 62 to 72 " +
    "percent, so that number stood out, and that is part of why I chose this paper to reproduce. " +
    "[IF ASKED which papers give the 62-72 band: say it is the range you saw across the papers in your literature " +
    "survey, that you have not compiled a formal citation table for it, and that you will tighten it before the " +
    "next review. DO NOT invent citations.]"
  );
}

// =========================================================================
// 5 — THE PAPER'S METHOD
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The base paper's method", "What I had to re-implement");

  bullets(s, [
    "Four base learners trained under 10-fold CV: SVM, RNN, ELM, Random Forest",
    "Each gets a weight  wᵢ = ½ (w_accuracy + w_diversity)   — Eq. (4)",
    "Accuracy weight, Eq. (5): normalised INVERSE of each learner's CV error — fewer mistakes, more weight",
    "Diversity weight, Eqs. (7)–(9): a 0/1 error vector per learner; sum the Euclidean distances to every other learner's; normalise",
    "Combine, Eq. (1):  ŷ = Σ wᵢ ŷᵢ  — a weighted sum",
  ], { y: 1.7, w: 7.5, fontSize: 15 });

  card(s, 8.4, 1.75, 4.3, 3.3);
  s.addText("Paper's own weights\n(their Table 8)", {
    x: 8.65, y: 1.95, w: 3.8, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: BERRY, lineSpacing: 20,
  });
  s.addText(
    [
      { text: "SVM        0.2516", options: { breakLine: true } },
      { text: "RNN        0.2286", options: { breakLine: true } },
      { text: "ELM        0.2168", options: { breakLine: true } },
      { text: "RF          0.3030", options: { bold: true, color: BERRY } },
    ],
    {
      x: 8.65, y: 2.8, w: 3.8, h: 1.6, isTextBox: true, margin: 0,
      fontFace: "Courier New", fontSize: 15, color: INK, lineSpacing: 26,
    }
  );
  s.addText("Remember 0.3030 — it returns on slide 14", {
    x: 8.65, y: 4.5, w: 3.8, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: ROSE, italic: true,
  });

  s.addNotes(
    "Their idea is that a learner should be trusted for two reasons: it is accurate, and it makes different " +
    "mistakes from the others. The accuracy weight is the normalised inverse of the cross-validation error, so " +
    "fewer mistakes means more weight. The diversity weight measures how far each learner's pattern of mistakes " +
    "sits from the others. The final weight is the average of the two, and the ensemble is the weighted sum. " +
    "[Remember 0.3030 — it is the most important number after 89.73.]"
  );
}

// =========================================================================
// 6 — OBJECTIVES + SUCCESS CRITERIA  (FRAMING LOCK)
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Objectives and success criteria", "How this project should be judged");

  bullets(s, [
    "Re-implement Ma et al.'s weighted ensemble under a classical-ML-only constraint",
    "Evaluate under their stated protocol: stratified 10-fold CV × 10 repeats = 100 fold-runs",
    "Compare per-class results against both Cortez (2009) and Ma (2024)",
    "Where results differ, diagnose the cause from evidence rather than tune to match",
  ], { y: 1.65, w: 12.1, fontSize: 15 });

  card(s, 0.6, 3.75, 12.1, 2.55, "F0E4E8");
  s.addText("This project is successful if:", {
    x: 0.95, y: 3.95, w: 11.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 17, bold: true, color: BERRY,
  });
  s.addText(
    [
      { text: "Every component the paper specifies is implemented as written — Eqs. (1) and (4)–(9), min-max preprocessing, 10-fold CV × 10 repeats", options: { bullet: true, breakLine: true } },
      { text: "The evaluation is leak-free and the protocol is stated precisely enough to be re-run", options: { bullet: true, breakLine: true } },
      { text: "Whatever number the method produces is reported as-is, with any discrepancy investigated rather than tuned away", options: { bullet: true } },
    ],
    {
      x: 0.95, y: 4.4, w: 11.4, h: 1.2, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, color: INK, paraSpaceAfter: 6, lineSpacing: 20,
    }
  );
  s.addText("It is NOT successful if we reach 89.73% by changing the protocol until the number moves.", {
    x: 0.95, y: 5.78, w: 11.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, bold: true, color: BERRY,
  });

  s.addNotes(
    "These are my objectives and, below them, the criteria I set for calling the project successful. " +
    "I want to be explicit about the third one, because it decides how you should read my results slide: " +
    "the goal was to implement the method faithfully and report what it produces, not to chase a target number. " +
    "If I had tuned the protocol until it hit 89.73 percent, that would have been the failure mode, not the success."
  );
}

// =========================================================================
// 7 — EXISTING VS PROPOSED
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Existing system vs. proposed system", "Where I followed the paper, and where I had to decide");

  tableOn(s, [
    hrow(["", "Existing — Ma et al. (2024)", "Proposed — this work"]),
    [{ text: "Base learners", options: { bold: true } }, "SVM, RNN, ELM, RF", "SVM, GradientBoosting, MLP, RF"],
    [{ text: "Scaling", options: { bold: true } }, "min-max (timing unstated)", "min-max inside a Pipeline, fit per training fold"],
    [{ text: "Class imbalance", options: { bold: true } }, "not stated", "balanced class weights on SVM and RF"],
    [{ text: "Reading of Eq. (1)", options: { bold: true } }, "ambiguous", "both soft and hard vote implemented"],
    [{ text: "Verification", options: { bold: true } }, "—", "the paper's own tables reconciled in code"],
  ], { y: 1.8, colW: [3.0, 4.4, 4.7] });

  s.addText(
    "Where the paper is silent or ambiguous, I made the choice explicit rather than guessing quietly.",
    { x: 0.6, y: 5.6, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, color: BERRY, italic: true }
  );

  s.addNotes(
    "The left column is what the paper specifies; the right is what I built. Two learners were substituted for " +
    "syllabus reasons, which I cover next. The other three rows are places where the paper is silent or ambiguous, " +
    "and instead of guessing quietly I made the choice explicit and, where the paper was genuinely ambiguous, " +
    "implemented both readings."
  );
}

// =========================================================================
// 8 — SUBSTITUTIONS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Syllabus substitutions", "Two learners are outside a classical-ML course");

  tableOn(s, [
    hrow(["Paper", "Why out of scope", "Substitute", "Why this one"]),
    ["SVM", "—", "SVC — unchanged", "already classical ML"],
    ["Random Forest", "—", "RandomForestClassifier — unchanged", "already classical ML"],
    ["RNN", "deep-learning sequence model; backprop-through-time", "GradientBoostingClassifier", "each new tree fits the residual errors of the previous ones — the in-syllabus analogue of iterative refinement"],
    ["ELM", "random FIXED hidden weights, closed-form output — explicitly not backprop", "MLPClassifier", "closest analogue that is still a neural net, but trained end-to-end by standard backpropagation"],
  ], { y: 1.75, colW: [1.7, 3.5, 3.0, 3.9], fontSize: 12 });

  card(s, 0.6, 5.15, 12.1, 0.95);
  s.addText(
    "Half the ensemble — SVM and Random Forest — is unchanged, including Random Forest, the strongest member in both their run and mine.",
    { x: 0.95, y: 5.4, w: 11.4, h: 0.5, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, bold: true, color: BERRY }
  );

  s.addNotes(
    "Two of the four learners are outside a classical-ML syllabus, so I substituted them. A recurrent network " +
    "refines its state step by step, and gradient boosting is the classical analogue: each new tree fits the errors " +
    "the previous trees made. An extreme learning machine is a neural net whose hidden weights are random and frozen, " +
    "so the closest in-syllabus analogue is a standard MLP trained by backpropagation. The important point is the box " +
    "at the bottom: SVM and Random Forest are untouched, including Random Forest, which is the strongest learner in " +
    "both the paper and my run — so the substitutions cannot be what explains the gap. [Say this deliberately.]"
  );
}

// =========================================================================
// 9 — DATASET
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Dataset", "UCI Wine Quality (Red) — the same 1,599 samples the paper uses");

  s.addChart(
    pres.ChartType.bar,
    [{ name: "Samples", labels: ["3", "4", "5", "6", "7", "8"], values: [10, 53, 681, 638, 199, 18] }],
    {
      x: 0.6, y: 1.7, w: 7.1, h: 4.2,
      barDir: "col", showTitle: true, title: "Samples per quality class",
      titleFontFace: HEAD, titleFontSize: 14, titleColor: BERRY,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: INK,
      chartColors: [BERRY],
      showLegend: false,
      catAxisLabelColor: MUTED, valAxisLabelColor: MUTED,
      catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
      valGridLine: { color: "EDE4E7", size: 1 },
      catGridLine: { style: "none" },
      barGapWidthPct: 60,
    }
  );

  bullets(s, [
    "1,599 samples · 11 features · quality 3–8",
    "Classes 5 and 6 alone are 82.5% of the data",
    "Classes 3 and 8 together are 1.75% — 10 and 18 samples",
    "Under 10-fold CV that is about ONE class-3 sample per test fold",
    "No class dropped, no class merged — all six retained, as in the paper",
  ], { x: 8.1, y: 1.9, w: 4.6, fontSize: 14 });

  s.addNotes(
    "This is the same 1,599-sample red wine dataset the paper uses. The imbalance is the defining property: " +
    "classes five and six are over eighty percent of the data, while class three has ten samples and class eight " +
    "has eighteen. Under ten-fold cross-validation that is about one class-three sample per test fold. I kept all " +
    "six classes rather than merging them into good and bad, because the paper reports all six and I wanted the " +
    "comparison to be like-for-like."
  );
}

// =========================================================================
// 10 — ARCHITECTURE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "System architecture", "One command; everything inside the box runs 100 times");

  // input
  card(s, 0.6, 1.65, 2.5, 0.85, "EAD9DF");
  s.addText("winequality-red.csv\n1599 × 11", {
    x: 0.6, y: 1.8, w: 2.5, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11.5, color: INK, align: "center", lineSpacing: 15,
  });

  // CV frame
  s.addShape(pres.ShapeType.roundRect, {
    x: 3.5, y: 1.55, w: 9.2, h: 3.55, rectRadius: 0.06,
    fill: { color: "FBF7F8" }, line: { color: ROSE, width: 1.25, dashType: "dash" },
  });
  s.addText("Stratified 10-fold CV  ×  10 repeats   =   100 fold-runs", {
    x: 3.7, y: 1.68, w: 8.8, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: ROSE,
  });

  // four learners
  const learners = ["SVM", "GradBoost\n(→ RNN)", "MLP\n(→ ELM)", "RF"];
  learners.forEach((name, i) => {
    const x = 3.8 + i * 2.2;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.15, w: 2.0, h: 0.95, rectRadius: 0.06,
      fill: { color: WHITE }, line: { color: "DCC9D0", width: 1 },
    });
    s.addText(name, {
      x, y: 2.28, w: 2.0, h: 0.7, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, bold: true, color: BERRY, align: "center", lineSpacing: 15,
    });
  });
  s.addText("each wrapped in  Pipeline([MinMaxScaler → estimator])  — scaler fit on the TRAIN fold only", {
    x: 3.8, y: 3.15, w: 8.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: BERRY, italic: true, align: "center",
  });

  // weights
  s.addShape(pres.ShapeType.roundRect, {
    x: 3.8, y: 3.55, w: 4.2, h: 1.35, rectRadius: 0.06,
    fill: { color: WHITE }, line: { color: "DCC9D0", width: 1 },
  });
  s.addText("0/1 error vector per learner  (Eq. 7)", {
    x: 3.9, y: 3.66, w: 4.0, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: MUTED, align: "center",
  });
  s.addText("w_accuracy (Eq. 5)     +     w_diversity (Eqs. 8–9)", {
    x: 3.9, y: 3.98, w: 4.0, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: INK, align: "center",
  });
  s.addText("wᵢ = ½(w_acc + w_div)   — Eq. (4)", {
    x: 3.9, y: 4.34, w: 4.0, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: BERRY, align: "center",
  });

  // combine
  s.addShape(pres.ShapeType.roundRect, {
    x: 8.3, y: 3.55, w: 4.1, h: 1.35, rectRadius: 0.06,
    fill: { color: WHITE }, line: { color: "DCC9D0", width: 1 },
  });
  s.addText("Eq. (1) — two readings", {
    x: 8.4, y: 3.66, w: 3.9, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: MUTED, align: "center",
  });
  s.addText("soft vote:  Σ wᵢ · Pᵢ", {
    x: 8.4, y: 3.98, w: 3.9, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: BERRY, align: "center",
  });
  s.addText("hard vote:  Σ wᵢ · onehot(ŷᵢ)", {
    x: 8.4, y: 4.32, w: 3.9, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, color: INK, align: "center",
  });

  // output
  card(s, 3.5, 5.35, 9.2, 0.8, "EAD9DF");
  s.addText("pooled confusion matrix  ·  per-class metrics  ·  reconciliation against the paper's tables", {
    x: 3.5, y: 5.57, w: 9.2, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12.5, color: INK, align: "center",
  });

  s.addText("preprocessing.py", { x: 0.6, y: 2.55, w: 2.5, h: 0.25, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, color: MUTED, align: "center" });
  s.addText("evaluate.py", { x: 3.5, y: 6.18, w: 9.2, h: 0.25, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, color: MUTED, align: "center" });

  s.addNotes(
    "This is the full pipeline. Data comes in, and everything inside the dashed box happens once per fold, a hundred " +
    "times in total. The four learners each produce out-of-fold predictions; from those I build a zero-one error " +
    "vector per learner, which feeds both the accuracy weight and the diversity weight. Those combine into the final " +
    "weight, and the weighted sum gives the ensemble prediction. The critical detail is that the scaler lives inside " +
    "the pipeline, so it only ever sees the training fold."
  );
}

// =========================================================================
// 11 — IMPLEMENTATION
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Implementation and protocol", "Reproducible from one command");

  bullets(s, [
    "Stack: Python 3, scikit-learn, pandas, NumPy, matplotlib. Single entry point: python run_all.py",
    "Protocol: stratified 10-fold CV × 10 repeats, seeds 0–9 → 100 fold-runs → 15,990 pooled predictions",
    "Class imbalance: class_weight='balanced' on SVM and RF — our own explicit choice; the paper states none",
    "Eq. (1) is ambiguous, so BOTH readings are implemented; the soft vote is the headline because it is the literal reading",
    "Every number in this deck is written to results/tables/*.csv by that one command — nothing typed by hand",
  ], { y: 1.65, w: 12.1, fontSize: 14.5 });

  card(s, 0.6, 4.35, 12.1, 1.75, "F0E4E8");
  s.addText("No data leakage — a bug I found and fixed in my own code", {
    x: 0.95, y: 4.55, w: 11.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: BERRY,
  });
  s.addText(
    "An earlier version min-max scaled all 1,599 rows once, then cross-validated. The scaling constants were " +
    "therefore computed using test-fold rows. Fixing it — moving MinMaxScaler inside the Pipeline — lowered my " +
    "scores. The numbers on the next slides are from the corrected version.",
    { x: 0.95, y: 4.95, w: 11.4, h: 1.0, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13.5, color: INK, lineSpacing: 19 }
  );

  s.addNotes(
    "Everything runs from a single command, and every number I show you is written to a CSV by that command, so it " +
    "is re-runnable. The most important implementation detail is the box at the bottom: the scaler sits inside the " +
    "pipeline so it only sees training data. An earlier version of my code scaled the whole dataset before " +
    "cross-validation, which leaks information from the test folds into the scaling constants and inflates the " +
    "accuracy. I found that, fixed it, and my scores went down — the numbers you are about to see are the corrected, " +
    "honest ones. [This slide is worth marks. Do not skip it for time.]"
  );
}

// =========================================================================
// 12 — RESULTS: RANKING
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Results — model ranking", "Pooled over 100 fold-runs (10-fold CV × 10 repeats)");

  s.addChart(
    pres.ChartType.bar,
    [{
      name: "Overall accuracy (%)",
      labels: ["MLP", "SVM", "GradBoost", "Ensemble (soft)", "Ensemble (hard)", "Random Forest"],
      values: [61.35, 61.95, 67.67, 69.01, 69.93, 71.03],
    }],
    {
      x: 0.6, y: 1.7, w: 7.5, h: 4.3,
      barDir: "bar", showTitle: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: INK,
      // Without an explicit format code the labels round to whole numbers,
      // which destroys the 2.02-point gap this slide exists to show.
      dataLabelFormatCode: "0.00",
      chartColors: [ROSE, ROSE, ROSE, BERRY, ROSE, GOLD],
      showLegend: false,
      catAxisLabelColor: INK, valAxisLabelColor: MUTED,
      catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
      valAxisMinVal: 55, valAxisMaxVal: 75,
      valGridLine: { color: "EDE4E7", size: 1 },
      catGridLine: { style: "none" },
      barGapWidthPct: 45,
    }
  );

  statCard(s, 8.5, 1.8, 4.2, "−2.02", "POINTS: OUR ENSEMBLE vs RANDOM FOREST", BERRY);

  bullets(s, [
    "Our ensemble beats 3 of its 4 members — but trails Random Forest",
    "The paper reports the opposite: their ensemble is 9.02 points ABOVE their best member",
    "Measured weights span only 0.2356 – 0.2698 — a maximum deviation of 0.0198 from a uniform 0.25",
  ], { x: 8.5, y: 3.55, w: 4.2, fontSize: 12.5 });

  s.addNotes(
    "Random Forest is the strongest single model at 71.03 percent. My ensemble reaches 69.01 percent, which beats " +
    "three of its four members but sits two points below Random Forest. The paper reports the opposite — their " +
    "ensemble is nine points above their best member. The last line is the clue that explains it: my computed weights " +
    "barely move away from a uniform quarter each, and I come back to that in two slides."
  );
}

// =========================================================================
// 13 — RESULTS: PER-CLASS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Results — per class, against both benchmarks", "Per-class values use the paper's own metric definition");

  s.addImage({ path: FIG, x: 0.6, y: 1.6, w: 7.3, h: 4.38 });

  tableOn(s, [
    hrow(["Class", "Cortez", "Ma", "Ours"]),
    ["3", "0.00", "33.33", "0.00"],
    ["4", "20.00", "63.16", "0.57"],
    ["5", "67.50", "84.80", "81.66"],
    ["6", "57.70", "88.06", "69.87"],
    ["7", "58.60", "77.08", "49.90"],
    ["8", "0.00", "50.00", "11.11"],
    [{ text: "Overall", options: { bold: true } }, { text: "—", options: { bold: true } }, { text: "89.73", options: { bold: true } }, { text: "69.01", options: { bold: true } }],
  ], { x: 8.2, y: 1.6, w: 4.5, colW: [1.2, 1.1, 1.1, 1.1], fontSize: 11.5 });

  s.addText(
    "The shape reproduces: mid-tier classes strong, extremes hardest — the paper's own conclusion. On class 5 we are within ~3 points.",
    { x: 8.2, y: 4.5, w: 4.5, h: 0.75, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: INK, lineSpacing: 17 }
  );
  s.addText(
    "Terminology finding: the paper calls this metric \"precision\", but its own Eq. (14) divides by the ACTUAL-class total — that is recall.",
    { x: 8.2, y: 5.3, w: 4.5, h: 0.8, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: BERRY, italic: true, lineSpacing: 17 }
  );

  s.addNotes(
    "This is the headline figure. Blue is the 2009 baseline, orange is the paper, green is mine. The qualitative shape " +
    "reproduces exactly: the two well-populated middle classes are predicted well and the rare extreme classes are the " +
    "hardest, which is the paper's own conclusion. On class five I am within about three points of them. " +
    "Class 4 at 0.57 percent is 53 samples sitting directly between the two dominant classes, so it gets absorbed by " +
    "them — that is the imbalance problem and it is my first item of future work. The last point is a separate finding: " +
    "the paper labels this metric precision, but their own worked example divides by the actual class total, which is " +
    "recall. I verified that by recomputing their table both ways."
  );
}

// =========================================================================
// 14 — CENTRAL FINDING  (PAYOFF)
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Why 89.73% does not reproduce", "Three independent checks, all computed from the paper's own printed tables");

  // check 1
  numCircle(s, 0.6, 1.62, 1);
  s.addText("Protocol mismatch", {
    x: 1.15, y: 1.62, w: 3.6, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: BERRY,
  });
  s.addText(
    "Their Table 9 confusion matrix sums to 491 samples — 30.7% of 1,599. That is a single hold-out split, not the " +
    "100-run cross-validation the text describes. Ours scores all 1,599 samples ten times over.",
    { x: 1.15, y: 2.0, w: 3.5, h: 1.5, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: INK, lineSpacing: 17 }
  );

  // check 2
  numCircle(s, 4.9, 1.62, 2);
  s.addText("Internal arithmetic", {
    x: 5.45, y: 1.62, w: 3.6, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: BERRY,
  });
  s.addText(
    "The diagonal of that same Table 9 is 403 of 491 = 82.08%, which is 7.65 points below the 89.73% stated in the " +
    "paper's own text.",
    { x: 5.45, y: 2.0, w: 3.5, h: 1.5, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: INK, lineSpacing: 17 }
  );

  // check 3
  numCircle(s, 9.2, 1.62, 3);
  s.addText("The weights are flat", {
    x: 9.75, y: 1.62, w: 3.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: BERRY,
  });
  s.addText(
    "Their Table 8 weights are never more than 0.053 from a uniform 0.25. Applied to their OWN base accuracies they " +
    "give 67.52%.",
    { x: 9.75, y: 2.0, w: 3.5, h: 1.5, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: INK, lineSpacing: 17 }
  );

  // the comparison
  card(s, 0.6, 3.5, 12.1, 1.35, "F0E4E8");
  s.addText("Weighted average of the paper's own base accuracies", {
    x: 0.95, y: 3.68, w: 6.4, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: INK,
  });
  s.addText("67.52%", {
    x: 7.4, y: 3.64, w: 1.7, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: INK,
  });
  s.addText("Our reproduction  →  1.49 points above it", {
    x: 0.95, y: 4.05, w: 6.4, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: BERRY,
  });
  s.addText("69.01%", {
    x: 7.4, y: 4.01, w: 1.7, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: BERRY,
  });
  s.addText("Paper's reported ensemble  →  22.21 points above it", {
    x: 0.95, y: 4.42, w: 6.4, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: ROSE,
  });
  s.addText("89.73%", {
    x: 7.4, y: 4.38, w: 1.7, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: ROSE,
  });
  s.addText(
    "Mechanism: with weights this flat, a weighted sum ≈ an unweighted average — which lands BETWEEN its members, never above the strongest.",
    { x: 9.3, y: 3.7, w: 3.2, h: 1.0, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: BERRY, italic: true, lineSpacing: 16 }
  );

  // caveat
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 5.05, w: 12.1, h: 1.1, rectRadius: 0.06,
    fill: { color: "FBF7F8" }, line: { color: ROSE, width: 1.25 },
  });
  s.addText(
    "Caveat: the Table 9 cells were transcribed by eye from the printed PDF and may contain reading errors — two of " +
    "the six per-class values do not reproduce, most plausibly for that reason. This is reported as \"we could not " +
    "reconcile these figures\", NOT as a claim that the paper is incorrect.",
    { x: 0.95, y: 5.22, w: 11.4, h: 0.8, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12.5, color: BERRY, lineSpacing: 17 }
  );

  s.addNotes(
    "Three independent checks, all computed in code from the paper's own printed tables. First, their confusion matrix " +
    "sums to 491 samples, about thirty percent of the dataset, which looks like a single hold-out split rather than the " +
    "hundred-run cross-validation the text describes. Second, the diagonal of that same table gives 82 percent, not the " +
    "89.73 the text states. Third, and this is the mechanism: their own weights are never more than 0.053 away from a " +
    "uniform quarter, and applying their weights to their own base accuracies gives 67.5 percent — my result sits one " +
    "and a half points above that, theirs sits twenty-two points above it. " +
    "I want to be clear that I transcribed that confusion matrix by eye from the PDF, so two of six values may be " +
    "reading errors on my part. I am reporting this as figures I could not reconcile, not as a claim that the paper " +
    "is wrong. [DELIVER THE CAVEAT CLEARLY — do not mumble it. It is what makes the other three claims credible.]"
  );
}

// =========================================================================
// 15 — CONCLUSION
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Conclusion", {
    x: 0.6, y: 0.45, w: 12.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: WHITE,
  });

  s.addText(
    [
      { text: "Structurally the reproduction succeeded", options: { bold: true, color: GOLD, breakLine: true } },
      { text: "All four base learners, Eqs. (1) and (4)–(9), min-max preprocessing and the 10×10 CV protocol were implemented as specified.", options: { color: "F0E4E8" } },
    ],
    { x: 0.6, y: 1.35, w: 5.9, h: 1.1, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, lineSpacing: 19 }
  );
  s.addText(
    [
      { text: "Numerically it did not", options: { bold: true, color: GOLD, breakLine: true } },
      { text: "69.01% against a reported 89.73%, and the ensemble does not overtake Random Forest.", options: { color: "F0E4E8" } },
    ],
    { x: 6.8, y: 1.35, w: 5.9, h: 1.1, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, lineSpacing: 19 }
  );

  s.addText("The gap is diagnosed, not excused.", {
    x: 0.6, y: 2.65, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 18, bold: true, color: WHITE,
  });
  s.addText(
    "Methodological lesson: an accuracy-and-diversity weighting scheme that normalises across learners of similar " +
    "error rates produces weights too flat for a strong learner to dominate — so on an imbalanced multiclass problem " +
    "it averages toward its members rather than exceeding the best of them.",
    { x: 0.6, y: 3.1, w: 12.1, h: 0.9, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, color: "F0E4E8", lineSpacing: 20 }
  );

  s.addText("Four contributions", {
    x: 0.6, y: 4.2, w: 12.1, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 17, bold: true, color: GOLD,
  });
  const contribs = [
    ["1", "A leak-free, single-command reproducible implementation"],
    ["2", "A three-check diagnosis of the discrepancy, from the paper's own tables"],
    ["3", "A terminology correction: the paper's \"precision\" is numerically recall"],
    ["4", "Both readings of an ambiguous Eq. (1) implemented and compared"],
  ];
  contribs.forEach(([n, t], i) => {
    const y = 4.68 + i * 0.47;
    s.addText(n + ".", {
      x: 0.6, y, w: 0.35, h: 0.35, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 14, bold: true, color: GOLD,
    });
    s.addText(t, {
      x: 1.0, y, w: 11.7, h: 0.35, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, color: WHITE,
    });
  });

  s.addNotes(
    "My summary is that the reproduction succeeded structurally and did not reproduce numerically, and the second part " +
    "is the informative one. Everything the paper specifies was implemented as written. The methodological lesson is " +
    "that when you normalise weights across four learners with broadly similar error rates, the weights come out nearly " +
    "uniform, and a nearly uniform weighted sum is just an average — which lands between your models, not above your " +
    "best one. That is a general property of the scheme, not something specific to my code."
  );
}

// =========================================================================
// 16 — FUTURE WORK + REFERENCES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Future work and references", "");

  s.addText("Future work", {
    x: 0.6, y: 1.5, w: 6.0, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 18, bold: true, color: BERRY,
  });
  bullets(s, [
    "Imbalance: SMOTE / ADASYN or cost-sensitive loss, targeted at classes 3, 4 and 8",
    "Statistical rigour: paired t-test or Wilcoxon across the 100 fold-runs — currently point estimates, no confidence intervals",
    "Weight sharpening: add a temperature to Eqs. (5) and (9) to test the flat-weight diagnosis directly — it predicts the ensemble should overtake RF once weights are sharp enough",
    "Generalisation: repeat on the 4,898-sample white wine set (already in data/raw/)",
    "Obtain the publisher's machine-readable Table 9 to remove the transcription caveat",
  ], { x: 0.6, y: 1.95, w: 6.2, fontSize: 12.5 });

  s.addText("References", {
    x: 7.2, y: 1.5, w: 5.5, h: 0.35, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 18, bold: true, color: BERRY,
  });
  s.addText(
    [
      { text: "[1]  Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to table: Uncovering wine quality for sales management through machine learning. Journal of Business Research, 176, 114576.", options: { breakLine: true } },
      { text: "[2]  Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. Decision Support Systems, 47(4), 547–553.", options: { breakLine: true } },
      { text: "[3]  UCI Machine Learning Repository — Wine Quality Dataset.", options: { breakLine: true } },
      { text: "[4]  Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. JMLR, 12, 2825–2830.", options: {} },
    ],
    { x: 7.2, y: 1.95, w: 5.5, h: 4.0, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11, color: INK, paraSpaceAfter: 10, lineSpacing: 15 }
  );

  s.addText("Thank you — questions welcome.", {
    x: 0.6, y: 6.3, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: BERRY,
  });

  s.addNotes(
    "The most direct next step is handling the imbalance properly with resampling, because that is what limits classes " +
    "three, four and eight. The second is statistical testing across my hundred fold-runs so I can report confidence " +
    "intervals rather than point estimates. The third is the most interesting: deliberately sharpening the weights to " +
    "test my own explanation — if the flat-weight diagnosis is right, sharpening them should let the ensemble overtake " +
    "Random Forest. Thank you, I am happy to take questions."
  );
}

// =========================================================================
// BACKUP SLIDES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Backup 1 — Confusion matrices", "Pooled over 100 fold-runs (15,990 predictions)");

  s.addText("Ensemble (soft vote)", {
    x: 0.6, y: 1.6, w: 5.9, h: 0.3, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 14, bold: true, color: BERRY,
  });
  tableOn(s, [
    hrow(["true \\ pred", "3", "4", "5", "6", "7", "8"]),
    ["3", "0", "9", "70", "21", "0", "0"],
    ["4", "1", "3", "372", "144", "10", "0"],
    ["5", "4", "11", "5561", "1202", "31", "1"],
    ["6", "3", "17", "1533", "4458", "360", "9"],
    ["7", "0", "0", "114", "874", "993", "9"],
    ["8", "0", "0", "0", "96", "64", "20"],
  ], { x: 0.6, y: 1.95, w: 5.9, colW: [1.15, 0.79, 0.79, 0.79, 0.79, 0.79, 0.8], fontSize: 11 });

  s.addText("Random Forest", {
    x: 6.8, y: 1.6, w: 5.9, h: 0.3, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 14, bold: true, color: BERRY,
  });
  tableOn(s, [
    hrow(["true \\ pred", "3", "4", "5", "6", "7", "8"]),
    ["3", "0", "2", "80", "18", "0", "0"],
    ["4", "8", "0", "344", "169", "9", "0"],
    ["5", "0", "11", "5582", "1201", "16", "0"],
    ["6", "0", "12", "1346", "4740", "282", "0"],
    ["7", "0", "0", "89", "883", "1016", "2"],
    ["8", "0", "0", "0", "90", "70", "20"],
  ], { x: 6.8, y: 1.95, w: 5.9, colW: [1.15, 0.79, 0.79, 0.79, 0.79, 0.79, 0.8], fontSize: 11 });

  s.addText(
    "Row sums are 10× the dataset class counts because predictions are pooled across the 10 repeats (1,599 × 10 = 15,990). " +
    "Class 4 at 0.57% is literally 3 correct out of 530; class 8 at 11.11% is 20 out of 180.",
    { x: 0.6, y: 5.5, w: 12.1, h: 0.8, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: MUTED, lineSpacing: 17 }
  );
  s.addNotes("Pull this out if asked to show the confusion matrix, or to prove the class-3 result.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 2 — Full per-class metrics", "Conventional precision, recall and specificity (%)");

  tableOn(s, [
    hrow(["Model", "Metric", "3", "4", "5", "6", "7", "8"]),
    ["Ensemble (soft)", "precision", "0.00", "7.50", "72.69", "65.61", "68.11", "51.28"],
    ["", "recall", "0.00", "0.57", "81.66", "69.87", "49.90", "11.11"],
    ["", "specificity", "99.95", "99.76", "77.24", "75.68", "96.68", "99.88"],
    ["Random Forest", "precision", "0.00", "0.00", "75.02", "66.75", "72.94", "90.91"],
    ["", "recall", "0.00", "0.00", "81.97", "74.29", "51.06", "11.11"],
    ["GradBoost", "recall", "0.00", "2.64", "78.41", "68.75", "53.27", "11.11"],
    ["SVM", "recall", "0.00", "0.00", "76.81", "65.19", "25.93", "0.00"],
    ["MLP", "recall", "2.00", "0.94", "74.99", "61.39", "39.15", "0.00"],
  ], { y: 1.75, colW: [2.5, 2.0, 1.27, 1.27, 1.27, 1.27, 1.27, 1.25], fontSize: 11 });

  s.addText(
    "The paper reports only its \"precision\" metric, which is numerically the recall row above. Full tables: results/tables/metrics_*.csv",
    { x: 0.6, y: 5.6, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: MUTED }
  );
  s.addNotes("Pull this out if asked about precision rather than just the paper's metric.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 3 — Optional unsupervised extension", "Not part of the reproduction; kept behind a --with-novelty flag");

  bullets(s, [
    "Clustering (K-means / Ward, k = 3..8): best silhouette 0.211 at K-means k=3 — but k=6 and k=7 are within 0.001, so it is effectively a tie",
    "Outlier detection: Isolation Forest and LOF both flag class 3 at 20.0%, roughly twice the ~7–10% of classes 5 and 6 — the rare classes are genuinely atypical, not merely few",
    "Class 8 is method-dependent — 33.3% under Isolation Forest but 5.6% under LOF",
    "Cluster-ID fed back as a 12th feature: NO improvement on the three target classes (3, 4, 8 all exactly 0.00 change); classes 5 and 6 declined, class 7 rose 0.50 — reported as a negative result",
    "FP-Growth association rules recover all four attributes the paper highlights (alcohol, sulphates, volatile acidity, citric acid), plus five more",
  ], { y: 1.7, w: 12.1, fontSize: 13.5 });

  s.addText(
    "Note: the cluster-feedback comparison was produced by a 2-repeat smoke run, not the 10-repeat canonical protocol, so its baseline column differs slightly from the headline per-class table.",
    { x: 0.6, y: 5.6, w: 12.1, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: MUTED, italic: true, lineSpacing: 16 }
  );
  s.addNotes(
    "Only present this if asked about extra or unsupervised work. It is not the contribution, and discussing " +
    "silhouette scores or lift invites questions on work that is not central to the reproduction."
  );
}

{
  const s = pres.addSlide();
  title(s, "Backup 4 — Table 9 reconciliation detail", "Recomputing the paper's per-class values from its own confusion matrix");

  tableOn(s, [
    hrow(["Class", "Paper reports", "Recomputed column-wise", "Recomputed row-wise", "Column-wise match?"]),
    ["3", "33.33", "33.33", "33.33", "yes (exact)"],
    ["4", "63.16", "63.16", "54.55", "yes (exact)"],
    ["5", "84.80", "84.80", "86.93", "yes (exact)"],
    ["6", "88.06", "88.50", "87.62", "within 0.6"],
    ["7", "77.08", "61.67", "60.66", "no"],
    ["8", "50.00", "60.00", "75.00", "no"],
  ], { y: 1.75, colW: [1.5, 2.4, 3.2, 2.6, 2.4], fontSize: 12 });

  bullets(s, [
    "4 of 6 reproduce column-wise (3 of them exactly); only 1 of 6 reproduces row-wise",
    "Column-wise = TP ÷ actual-class total = recall — confirming the terminology finding empirically",
    "The two non-matching classes (7 and 8) are most plausibly my own transcription errors from the printed PDF",
  ], { y: 4.4, w: 12.1, fontSize: 13.5 });

  s.addNotes("Pull this out if the panel wants to see the reconciliation arithmetic itself.");
}

pres.writeFile({ fileName: path.join(__dirname, "first_review.pptx") })
  .then((f) => console.log("wrote " + f));
