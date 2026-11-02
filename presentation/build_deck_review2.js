/**
 * build_deck_review2.js — generates second_review.pptx
 *
 * Unlike the Review-1 deck, no result is typed in by hand: every number is read
 * from results/review2/tables/*.csv (and results/tables/ for the Review-1
 * baseline) when the deck is built. Wherever the wording depends on an outcome
 * ("overtakes" vs "comes within"), it is computed from the data too. Re-run the
 * pipeline, re-run this script, and the deck stays correct.
 *
 *   node build_deck_review2.js
 *   REVIEW2_DIR=/some/other/run node build_deck_review2.js   # build from another run
 */
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.join(__dirname, "..");
const R2 = process.env.REVIEW2_DIR || path.join(ROOT, "results", "review2");
const OUT = process.env.DECK_OUT || path.join(__dirname, "second_review.pptx");

// ---- data ----------------------------------------------------------------
function parseLine(line) {
  const out = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c;
    } else if (c === '"') q = true;
    else if (c === ",") { out.push(cur); cur = ""; }
    else cur += c;
  }
  out.push(cur);
  return out;
}
function readCsv(file) {
  const lines = fs.readFileSync(file, "utf8").trim().split(/\r?\n/);
  const head = parseLine(lines[0]);
  return lines.slice(1).map((l) => {
    const v = parseLine(l), o = {};
    head.forEach((h, i) => { o[h] = v[i]; });
    return o;
  });
}
const T = (f) => readCsv(path.join(R2, "tables", f));
const FIG = (f) => path.join(R2, "figures", f);
const num = (x) => parseFloat(x);
const f2 = (x) => num(x).toFixed(2);
const f1 = (x) => num(x).toFixed(1);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const signed = (x, d = 2) => (num(x) >= 0 ? "+" : "−") + Math.abs(num(x)).toFixed(d);

const A = T("A_class_balancing.csv");
const B1 = T("B1_weight_temperature.csv");
const B = T("B2_B3_improvements.csv");
const CHOSEN = T("B4_chosen_temperatures.csv");
const COMP = T("model_comparison.csv");
const HEADLINE = T("headline_review1_vs_review2.csv");
const BEST_NAME = fs.readFileSync(path.join(R2, "tables", "headline_best_model.txt"), "utf8").trim();
const FI = T("C_feature_importance.csv");
const CROSS = T("C_paper_crosscheck.csv");
const SUBSET = T("C_feature_subset.csv");
const AGREE = T("C_ranking_agreement.csv");
const CM1 = T("confusion_matrix_review1_ensemble.csv");
const CM2 = T("confusion_matrix_review2_best.csv");
const R1SUM = readCsv(path.join(ROOT, "results", "tables", "model_accuracy_summary.csv"));
const PAIRED = T("paired_comparison.csv");

const ENS = "Ensemble (paper weights)";
const LABEL = {
  none: "No balancing", partial: "Review 1 (SVM + RF only)",
  class_weight: "Class weights, all four", smote: "SMOTE oversampling",
};
const ens = (b) => A.find((r) => r.balancing === b && r.model === ENS);
const learner = (b, m) => A.find((r) => r.balancing === b && r.model === m);
const bRow = (name) => B.find((r) => r.model === name);

const r1Ens = ens("partial");
const r1Rf = learner("partial", "RF");
const r1Canon = num(R1SUM.find((r) => r.model === "Ensemble (soft vote)").overall_accuracy_pct);
const regressionOk = Math.abs(num(r1Ens.accuracy) - r1Canon) < 1e-3;

const bestBalancing = ["none", "partial", "class_weight", "smote"]
  .map((b) => ens(b)).sort((a, b) => num(b.macro_f1) - num(a.macro_f1))[0].balancing;

const best = COMP[0];
const bestAcc = [...COMP].sort((a, b) => num(b.accuracy) - num(a.accuracy))[0];
const ltR1 = bRow("Learned-temperature ensemble | " + LABEL.partial);
const ltSm = bRow("Learned-temperature ensemble | " + LABEL.smote);
const stack4 = bRow("Stacked: paper's 4 learners (class-weighted)");

// Weight-sharpening sweep (Review-1 members).
const sweepAcc = B1.filter((r) => r.balancing === "partial" && r.sharpen === "accuracy")
  .map((r) => ({ T: num(r.temperature), acc: num(r.accuracy), w: num(r.largest_weight) }));
const sweepBoth = B1.filter((r) => r.balancing === "partial" && r.sharpen === "both")
  .map((r) => ({ T: num(r.temperature), acc: num(r.accuracy), w: num(r.largest_weight) }));
const rfAcc = num(B1.find((r) => r.balancing === "partial").rf_accuracy);
const sweepBest = [...sweepAcc].sort((a, b) => b.acc - a.acc)[0];
const firstOvertake = sweepAcc.find((r) => r.acc > rfAcc);
const bothPeak = [...sweepBoth].sort((a, b) => b.acc - a.acc)[0];
const bothLast = sweepBoth[sweepBoth.length - 1];

// Temperatures chosen by the inner CV in route 2.
const chosenFor = (b) => CHOSEN.filter((r) => r.balancing === b);
const shareAtLeast = (b, t) => {
  const rows = chosenFor(b);
  return Math.round((100 * rows.filter((r) => num(r.temperature) >= t).length) / rows.length);
};
const nFolds = chosenFor("partial").length;

const headRow = (m) => HEADLINE.find((r) => r.metric === m);
const R1_ENS_NAME = ENS + " | " + LABEL.partial;
const R1_RF_NAME = "RF | " + LABEL.partial;
const LT_R1_NAME = "Learned-temperature ensemble | " + LABEL.partial;
const pair = (a, b, metric) => PAIRED.find((r) => r.model === a && r.compared_with === b && r.metric === metric);
const pfmt = (p) => (num(p) < 0.001 ? "< 0.001" : num(p).toFixed(3));
const wins = (r) => `${r.repeats_won} of ${r.repeats}`;
const fiTop = FI.slice(0, 4).map((r) => r.feature);
const crossIn = CROSS.filter((r) => r.in_our_top4 === "True").map((r) => r.paper_attribute);
const crossOut = CROSS.filter((r) => r.in_our_top4 !== "True");
const sub = (k) => SUBSET.find((r) => r.subset === `top ${k} (chosen in-fold)`);
const paper4 = SUBSET.find((r) => r.subset.startsWith("Ma et al."));
const full11 = sub(11);
const top4 = sub(4);

// Shorter display names for tables and charts.
function short(name) {
  return name
    .replace("Ensemble (paper weights) | ", "Paper ensemble · ")
    .replace("Learned-temperature ensemble | ", "Learned-T ensemble · ")
    .replace("Review 1 (SVM + RF only)", "Review-1 setup")
    .replace("Class weights, all four", "class weights")
    .replace("SMOTE oversampling", "SMOTE")
    .replace("No balancing", "no balancing")
    .replace(" | ", " · ");
}

// ---- palette (shared with the Review-1 deck) -------------------------------
const BERRY = "6D2E46", ROSE = "A26769", GOLD = "C8A45C", INK = "2B2B2B", MUTED = "6E6E6E";
const TINT = "F5EFF1", WHITE = "FFFFFF", PALE = "F0E4E8";
const HEADF = "Cambria", BODY = "Calibri";
const SAFE_BOTTOM = 7.2;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "SURIANANDHAN S";
pres.title = "Wine Quality Prediction Using a Weighted Ensemble — Second Review";

// ---- helpers -------------------------------------------------------------
function title(slide, text, subtitle) {
  slide.addText(text, { x: 0.6, y: 0.35, w: 12.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 30, bold: true, color: BERRY });
  if (subtitle) slide.addText(subtitle, { x: 0.6, y: 1.03, w: 12.1, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: MUTED, italic: true });
}
function bullets(slide, items, opts) {
  const o = Object.assign({ x: 0.6, y: 1.6, w: 7.2, h: 4.6, fontSize: 15 }, opts || {});
  const h = Math.min(o.h, SAFE_BOTTOM - o.y);
  slide.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i !== items.length - 1 } })),
    { x: o.x, y: o.y, w: o.w, h, isTextBox: true, margin: 0, valign: "top",
      fontFace: BODY, fontSize: o.fontSize, color: INK, paraSpaceAfter: 9, lineSpacing: o.lineSpacing || 21 });
}
function text(slide, t, x, y, w, h, opts) {
  slide.addText(t, Object.assign({ x, y, w, h: Math.min(h, SAFE_BOTTOM - y), isTextBox: true, margin: 0,
    valign: "top", fontFace: BODY, fontSize: 13, color: INK, lineSpacing: 18 }, opts || {}));
}
function card(slide, x, y, w, h, fill, line) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08,
    fill: { color: fill || TINT }, line: { color: line || fill || TINT, width: line ? 1.25 : 0 } });
}
function statCard(slide, x, y, w, value, label, valColor, fill) {
  card(slide, x, y, w, 1.45, fill || TINT);
  slide.addText(value, { x, y: y + 0.15, w, h: 0.72, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 34, bold: true, color: valColor || BERRY, align: "center" });
  slide.addText(label, { x: x + 0.15, y: y + 0.9, w: w - 0.3, h: 0.45, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: MUTED, align: "center" });
}
function numCircle(slide, x, y, n, fill) {
  slide.addShape(pres.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42,
    fill: { color: fill || BERRY }, line: { color: fill || BERRY, width: 0 } });
  slide.addText(String(n), { x, y: y + 0.03, w: 0.42, h: 0.36, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 15, bold: true, color: WHITE, align: "center" });
}
function tableOn(slide, rows, opts) {
  const o = Object.assign({ x: 0.6, y: 1.7, w: 12.1, fontSize: 12 }, opts || {});
  slide.addTable(rows, { x: o.x, y: o.y, w: o.w, colW: o.colW, fontFace: BODY, fontSize: o.fontSize,
    color: INK, border: { type: "solid", color: "E3D8DC", pt: 1 }, align: "left", valign: "middle",
    autoPage: false, rowH: o.rowH });
}
function hrow(cells) {
  return cells.map((c) => ({ text: c, options: { bold: true, color: WHITE, fill: { color: BERRY }, fontSize: 11.5 } }));
}
function boldRow(cells, fill) {
  return cells.map((c) => ({ text: c, options: { bold: true, fill: { color: fill || PALE } } }));
}
function image(slide, file, x, y, w, h) {
  if (!fs.existsSync(file)) throw new Error("missing figure: " + file);
  slide.addImage({ path: file, x, y, w, h });
}

// =========================================================================
// 1 — TITLE
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Wine Quality Prediction\nUsing a Weighted Ensemble", { x: 0.9, y: 1.2, w: 11.5, h: 1.8,
    isTextBox: true, margin: 0, fontFace: HEADF, fontSize: 40, bold: true, color: WHITE, lineSpacing: 46 });
  s.addText("Review 2 — class balancing, improving the result, and feature importance", {
    x: 0.9, y: 3.05, w: 11.5, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 16, color: GOLD, italic: true });
  s.addText("Building on a reproduction of Ma et al. (2024), Journal of Business Research 176:114576", {
    x: 0.9, y: 3.45, w: 11.5, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: "E8DCE1" });
  s.addText([
    { text: "SURIANANDHAN S", options: { bold: true, fontSize: 19, breakLine: true } },
    { text: "127018060", options: { fontSize: 15, color: "E8DCE1", breakLine: true } },
    { text: "CSE425 — Machine Learning Essentials", options: { fontSize: 14, color: "E8DCE1" } },
  ], { x: 0.9, y: 4.25, w: 6.0, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE });
  s.addText([
    { text: "Guide", options: { fontSize: 11, color: GOLD, breakLine: true } },
    { text: "Dr. Vidivelli S, AP-II", options: { bold: true, fontSize: 15, breakLine: true } },
    { text: "Department of CSE, School of Computing", options: { fontSize: 13, color: "E8DCE1" } },
  ], { x: 7.2, y: 4.25, w: 5.2, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE });
  s.addText("Second Review", { x: 0.9, y: 6.35, w: 5, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: GOLD });
  s.addNotes(
    "Good morning. At the first review I presented a faithful reproduction of a 2024 Journal of Business Research " +
    "paper on predicting wine quality with a weighted ensemble. You asked for three things: class balancing, an " +
    "improved result, and feature importance. This review covers all three, in that order.");
}

// =========================================================================
// 2 — WHERE REVIEW 1 LEFT OFF + THE THREE ASKS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Where Review 1 left off", "The baseline, the diagnosis, and the three changes requested");

  statCard(s, 0.6, 1.6, 3.0, f2(r1Ens.accuracy) + "%", "REVIEW-1 ENSEMBLE (FAITHFUL REPRODUCTION)", BERRY);
  statCard(s, 3.8, 1.6, 3.0, f2(r1Rf.accuracy) + "%", "RANDOM FOREST ALONE — BEAT THE ENSEMBLE", ROSE);
  statCard(s, 7.0, 1.6, 2.7, f1(r1Ens.recall_4) + "%", "CLASS-4 RECALL — RARE CLASSES IGNORED", ROSE);
  statCard(s, 9.9, 1.6, 2.8, "≈ 0.25", "EVERY WEIGHT — TOO FLAT TO HELP", BERRY);

  text(s, "Diagnosis at Review 1: the paper's weights come out nearly uniform, so the ensemble behaves like a plain " +
    "average — it lands between its members instead of above the best one.",
    0.6, 3.25, 12.1, 0.7, { fontSize: 13.5, italic: true, color: BERRY });

  tableOn(s, [
    hrow(["Requested at Review 1", "What Review 2 did", "Slides"]),
    ["1.  Class balancing — yet to be done", "Four balancing schemes compared on identical folds, incl. SMOTE inside the fold", "4 – 5"],
    ["2.  Improve the result", "Tested the Review-1 diagnosis, then fixed it: weights tuned by inner CV; stacking; stronger members", "6 – 10"],
    ["3.  Work on feature importance", "Permutation importance on held-out folds, checked against two other methods and the paper", "11 – 14"],
  ], { y: 4.1, colW: [3.6, 7.0, 1.5], fontSize: 12.5 });

  s.addNotes(
    `At Review 1 my faithful reproduction reached ${f2(r1Ens.accuracy)} percent, and Random Forest on its own did ` +
    `better at ${f2(r1Rf.accuracy)}. Two problems were visible. First, the rare quality classes were essentially ` +
    `ignored — class 4 recall was ${f1(r1Ens.recall_4)} percent. Second, the paper's weighting scheme produces ` +
    "weights that are all close to a quarter, so the ensemble just averages its members. You asked me to address " +
    "class balancing, improve the result, and work on feature importance. This table is the map for the rest of the talk.");
}

// =========================================================================
// 3 — HOW REVIEW 2 IS JUDGED
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "How Review 2 is judged", "Rules fixed in the code before any Review-2 experiment was run");

  const rules = [
    ["Same protocol as Review 1", "Stratified 10-fold CV × 10 repeats, the same fold seeds, every scaler and resampler fitted inside the training fold."],
    ["Review 1 is not rewritten", regressionOk
      ? `Review-1 numbers are unchanged. Re-run inside the new code, the Review-1 setup reproduces ${f2(r1Ens.accuracy)}% to every digit — so every comparison is like-for-like.`
      : "Review-1 numbers are unchanged and kept as the baseline."],
    ["Primary metric: macro-F1", "Averages F1 over all six quality classes with equal weight. Accuracy is still reported on every slide."],
  ];
  rules.forEach(([h, b], i) => {
    const y = 1.6 + i * 1.05;
    numCircle(s, 0.6, y, i + 1);
    text(s, h, 1.2, y - 0.02, 5.6, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
    text(s, b, 1.2, y + 0.35, 5.7, 0.7, { fontSize: 12.5, lineSpacing: 17 });
  });

  card(s, 7.3, 1.55, 5.4, 3.25, PALE);
  text(s, "Why not just accuracy?", 7.6, 1.75, 4.9, 0.35, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
  text(s,
    `The Review-1 ensemble scores ${f1(r1Ens.accuracy)}% accuracy while getting ${f1(r1Ens.recall_3)}% of ` +
    `class-3 wines and ${f1(r1Ens.recall_4)}% of class-4 wines right. Classes 5 and 6 are 82.5% of the data, so ` +
    "accuracy barely notices the rare grades. Class balancing deliberately trades a little of the common classes " +
    "for the rare ones — judging it on accuracy alone would judge it on the one thing it gives up.",
    7.6, 2.2, 4.9, 2.5, { fontSize: 12.5, lineSpacing: 17 });

  card(s, 0.6, 5.0, 12.1, 1.15, "FBF7F8", ROSE);
  text(s,
    "Disclosure: the winner is picked on the same cross-validation that scores it, which flatters its score slightly. " +
    "Two candidates were added after a 1-repeat smoke test; their settings are chosen inside each training fold, " +
    "never from the test folds. Both are stated rather than hidden.",
    0.9, 5.15, 11.5, 0.9, { fontSize: 12, color: BERRY, lineSpacing: 16 });

  s.addNotes(
    "Before running anything for Review 2, I fixed the rules in the code. Same protocol as Review 1, so the numbers " +
    "are comparable. The Review-1 numbers are unchanged — and as a check, the Review-1 configuration re-run " +
    "inside the new code reproduces the old number exactly. The primary metric is macro-F1, and the box on the right " +
    "is why: accuracy can be high while the rare classes are completely missed. I also want to be upfront about two " +
    "honest limitations, in the box at the bottom. [Say the disclosure — it pre-empts the hardest question.]");
}

// =========================================================================
// 4 — CLASS BALANCING: WHAT WAS TRIED
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Class balancing — four schemes, one variable",
    "Same four learners, same paper weighting, same folds — only the balancing changes");

  tableOn(s, [
    hrow(["Scheme", "What it does", "Where it acts"]),
    ["No balancing", "Every training sample counts equally — the rare classes are simply outvoted", "—"],
    ["Review 1", "'Balanced' class weights on SVM and Random Forest only", "Inside the loss"],
    ["Class weights, all four", "The same for MLP and GradBoost too. They have no class_weight option, so each sample gets the equivalent weight directly", "Inside the loss"],
    ["SMOTE oversampling", "Creates synthetic rare-class wines by interpolating between real neighbouring ones, until every class is equally represented", "Training fold only"],
  ], { y: 1.65, colW: [2.6, 7.4, 2.1], fontSize: 12.5 });

  card(s, 0.6, 4.75, 12.1, 1.45, PALE);
  text(s, "SMOTE without leakage", 0.95, 4.92, 6, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  text(s,
    "SMOTE sits inside the pipeline, after the scaler: training fold → scale → synthesise → fit. Synthetic wines are " +
    "built only from training-fold wines, and the test fold is never resampled — the same rule that fixed the " +
    "leakage bug at Review 1.",
    0.95, 5.3, 11.4, 0.85, { fontSize: 12.5, lineSpacing: 17 });

  s.addNotes(
    "I compared four balancing schemes, holding everything else fixed so that the balancing is the only thing that " +
    "changes. Class weights make mistakes on rare classes cost more during training. SMOTE instead creates new " +
    "synthetic examples of the rare classes. The important detail is in the box: SMOTE only ever sees the training " +
    "fold. If it saw the whole dataset, synthetic copies of test wines would leak into training — the same kind of " +
    "leakage I fixed at Review 1.");
}

// =========================================================================
// 5 — CLASS BALANCING: RESULTS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Class balancing — results", "Paper-weighted ensemble, pooled over 100 fold-runs");
  image(s, FIG("A_class_balancing.png"), 0.6, 1.5, 8.2, 3.15);

  const rows = ["none", "partial", "class_weight", "smote"].map((b) => {
    const r = ens(b);
    const cells = [LABEL[b], f2(r.accuracy), f2(r.macro_f1), f1(r.recall_4), f1(r.recall_7), f1(r.recall_8)];
    return b === bestBalancing ? boldRow(cells) : cells;
  });
  tableOn(s, [hrow(["Scheme", "Acc.", "Macro-F1", "Rec. 4", "Rec. 7", "Rec. 8"]), ...rows],
    { x: 0.6, y: 4.8, w: 8.2, colW: [2.9, 1.0, 1.15, 1.05, 1.05, 1.05], fontSize: 11.5 });

  const sm = ens("smote");
  text(s, "What it shows", 9.15, 1.55, 3.6, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    `${LABEL[bestBalancing]} gives the best macro-F1: ${f2(ens(bestBalancing).macro_f1)} vs ${f2(r1Ens.macro_f1)} at Review 1`,
    `Class-4 recall: ${f1(r1Ens.recall_4)}% → ${f1(sm.recall_4)}% with SMOTE; class 7: ${f1(r1Ens.recall_7)}% → ${f1(sm.recall_7)}%`,
    `The price: accuracy falls ${f2(num(r1Ens.accuracy) - num(sm.accuracy))} points, because the model now calls rare classes more often and some of those calls are wrong`,
    "Balancing moves recall from the crowded middle classes to the rare ones — it does not create information that isn't there",
  ], { x: 9.15, y: 1.95, w: 3.6, fontSize: 12, lineSpacing: 16 });

  s.addNotes(
    `On the left, accuracy and macro-F1 for each scheme; on the right, recall per quality class. ` +
    `${LABEL[bestBalancing]} gives the best macro-F1. The per-class view shows why: class 4 goes from ` +
    `${f1(r1Ens.recall_4)} percent to ${f1(sm.recall_4)} percent with SMOTE, and class 7 from ${f1(r1Ens.recall_7)} ` +
    `to ${f1(sm.recall_7)}. The cost is accuracy, which drops by ${f2(num(r1Ens.accuracy) - num(sm.accuracy))} ` +
    "points, because classes 5 and 6 lose some recall to the rare classes. That trade-off is the honest result of " +
    "class balancing — it redistributes accuracy towards the rare classes rather than adding it.");
}

// =========================================================================
// 6 — IMPROVING THE RESULT: FOUR ROUTES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Improving the result — four routes", "Each one tests a specific idea; one of them is the fix the Review-1 diagnosis points to");

  const routes = [
    ["Sharpen the weights", "Test", "Raise the paper's weights to a power T before normalising. Review 1 predicted sharper weights would let the ensemble overtake Random Forest.", "A diagnostic: the weights see the predictions they are scored on, so it is never used to pick the final model."],
    ["Learn the temperature", "Fix", "The same sharpening, but T is chosen inside each training fold by an inner 5-fold CV — the test fold is never involved.", "The leak-free version of route 1: a legitimate result."],
    ["Stacking", "Replace", "Throw away the hand-made weights; a logistic regression learns how to combine the members' probabilities.", "Also tried with a class-balanced combiner."],
    ["Stronger members", "Upgrade", "Add ExtraTrees and HistGradientBoosting, alone and combined with RF and SVM.", "Tests whether better members help more than better weighting."],
  ];
  routes.forEach(([h, tag, body, foot], i) => {
    const x = 0.6 + i * 3.08, y = 1.65, w = 2.9;
    card(s, x, y, w, 4.45, i === 1 ? PALE : TINT, i === 1 ? BERRY : null);
    numCircle(s, x + 0.2, y + 0.2, i + 1, i === 1 ? BERRY : ROSE);
    text(s, tag.toUpperCase(), x + 0.75, y + 0.27, 2.0, 0.3, { fontSize: 10.5, bold: true, color: i === 1 ? BERRY : MUTED });
    text(s, h, x + 0.2, y + 0.8, w - 0.4, 0.4, { fontFace: HEADF, fontSize: 15.5, bold: true, color: BERRY });
    text(s, body, x + 0.2, y + 1.3, w - 0.4, 1.9, { fontSize: 12, lineSpacing: 16 });
    text(s, foot, x + 0.2, y + 3.3, w - 0.4, 1.05, { fontSize: 11, italic: true, color: MUTED, lineSpacing: 15 });
  });

  s.addNotes(
    "I tried four routes to improve the result. The first two belong together. Route 1 tests my Review-1 diagnosis " +
    "directly by sharpening the paper's weights — but it is only a diagnostic, because the weights are computed from " +
    "the same predictions they are scored on. Route 2 is the fix done properly: the sharpening level is learned " +
    "inside each training fold, so the test data never influences it. Routes 3 and 4 are the standard alternatives: " +
    "learn the combination with stacking, or use stronger members.");
}

// =========================================================================
// 7 — TESTING THE REVIEW-1 PREDICTION
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Route 1 — testing the Review-1 prediction", "Sharpening the paper's weights with a temperature T  (T = 1 is the paper exactly)");
  image(s, FIG("B1_weight_temperature.png"), 0.6, 1.5, 12.1, 4.27);

  const overtakeLine = firstOvertake
    ? `Prediction holds: sharpening the accuracy term overtakes Random Forest from T = ${firstOvertake.T} (${firstOvertake.acc.toFixed(2)}% vs ${rfAcc.toFixed(2)}%) — a small margin, and only a diagnostic.`
    : `Sharpening the accuracy term peaks at ${sweepBest.acc.toFixed(2)}% (T = ${sweepBest.T}), ${(rfAcc - sweepBest.acc).toFixed(2)} below Random Forest — it closes most of the gap but does not overtake.`;
  card(s, 0.6, 5.85, 6.0, 1.25, PALE);
  text(s, overtakeLine, 0.85, 5.97, 5.6, 1.05, { fontSize: 12.5, bold: true, color: BERRY, lineSpacing: 17 });
  card(s, 6.75, 5.85, 5.95, 1.25, TINT);
  text(s,
    `Sharpening both terms peaks at T = ${bothPeak.T}, then falls to ${bothLast.acc.toFixed(2)}% at T = ${bothLast.T}: ` +
    "the diversity weight concentrates on the learner whose mistakes differ most — usually the weakest one.",
    6.95, 5.97, 5.6, 1.05, { fontSize: 12, lineSpacing: 16 });

  s.addNotes(
    "At Review 1, my future-work slide predicted that if the flat weights were the problem, sharpening them should " +
    "let the ensemble catch Random Forest. This chart tests that. The dashed line is Random Forest on its own. " +
    (firstOvertake
      ? `Sharpening the accuracy part of the weights crosses that line from T equals ${firstOvertake.T}. `
      : `Sharpening the accuracy part closes most of the gap, peaking ${(rfAcc - sweepBest.acc).toFixed(2)} points below it. `) +
    "Sharpening both parts eventually backfires, which is itself informative: the diversity weight rewards the " +
    "learner whose mistakes are most different, and that is usually the weakest learner. I treat this chart as a " +
    "diagnostic only, because here the weights are computed from the same predictions they are scored on. The next " +
    "slide is the leak-free version.");
}

// =========================================================================
// 8 — THE FIX: LEARNED TEMPERATURE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Route 2 — the fix, done properly", "Temperature chosen inside each training fold by an inner 5-fold CV — never sees the test fold");

  const beatRf = num(ltR1.accuracy) > num(r1Rf.accuracy);
  statCard(s, 0.6, 1.6, 3.0, f2(r1Ens.accuracy) + "%", "REVIEW-1 ENSEMBLE (T = 1)", MUTED);
  statCard(s, 3.8, 1.6, 3.0, f2(ltR1.accuracy) + "%", "LEARNED-T ENSEMBLE, SAME MEMBERS", BERRY);
  statCard(s, 7.0, 1.6, 2.7, f2(r1Rf.accuracy) + "%", "RANDOM FOREST ALONE", ROSE);
  statCard(s, 9.9, 1.6, 2.8, shareAtLeast("partial", 10) + "%", `OF ${nFolds} FOLDS CHOSE T ≥ 10`, BERRY);

  bullets(s, [
    `Same four learners as Review 1, only the weighting changes: accuracy ${f2(r1Ens.accuracy)}% → ${f2(ltR1.accuracy)}% ` +
      `(${signed(num(ltR1.accuracy) - num(r1Ens.accuracy))}), macro-F1 ${f2(r1Ens.macro_f1)} → ${f2(ltR1.macro_f1)}`,
    beatRf
      ? `It now beats Random Forest (${f2(r1Rf.accuracy)}%) — the ensemble finally does what an ensemble should`
      : (() => {
        const pr = pair(LT_R1_NAME, R1_RF_NAME, "accuracy");
        const losses = num(pr.repeats) - num(pr.repeats_won) - num(pr.repeats_tied);
        return `It closes ${f2(num(ltR1.accuracy) - num(r1Ens.accuracy))} of the ${f2(num(r1Rf.accuracy) - num(r1Ens.accuracy))}-point ` +
          `gap to Random Forest — now a statistical tie with it (${pr.repeats_won} wins, ${pr.repeats_tied} ties, ${losses} losses across repeats)`;
      })(),
    `Not noise: it beats the Review-1 ensemble on accuracy in ${wins(pair(LT_R1_NAME, R1_ENS_NAME, "accuracy"))} repeats, on identical folds`,
    `The inner CV, left to itself, picks a sharp temperature (T ≥ 10) in ${shareAtLeast("partial", 10)}% of folds — independent confirmation that the paper's T = 1 is too flat`,
    `With SMOTE members as well: macro-F1 ${f2(ltSm.macro_f1)}, accuracy ${f2(ltSm.accuracy)}% — the class-balanced version of the same fix`,
  ], { y: 3.3, w: 7.0, fontSize: 12.5, lineSpacing: 17 });

  // How often the inner CV picked each temperature -- the evidence behind the 4th stat card.
  // An image, not a native chart: Keynote and Google Slides drop pptxgenjs charts.
  image(s, FIG("B4_chosen_temperatures.png"), 7.9, 3.25, 4.8, 3.33);

  s.addNotes(
    "This is the main improvement, and it follows directly from the Review-1 diagnosis. The weighting formula is the " +
    "paper's, but instead of a fixed temperature of 1, each training fold runs its own inner cross-validation to pick " +
    "the temperature. The outer test fold never influences that choice, so this is a fair result. With exactly the " +
    `same four learners, accuracy moves from ${f2(r1Ens.accuracy)} to ${f2(ltR1.accuracy)} percent. ` +
    `And notice the last statistic: left to choose for itself, the inner CV picks a sharp temperature in ` +
    `${shareAtLeast("partial", 10)} percent of folds. That is the data independently agreeing with my Review-1 diagnosis.`);
}

// =========================================================================
// 9 — EVERY CANDIDATE: THE TRADE-OFF
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Every candidate — no model wins both metrics",
    `${COMP.length} models and ensembles, each pooled over 100 fold-runs`);
  image(s, FIG("B_tradeoff.png"), 0.6, 1.45, 8.3, 4.9);

  text(s, "Reading the chart", 9.2, 1.5, 3.5, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    "Right = better on the common classes; up = better on all six equally",
    "The dashed frontier: models no other model beats on both at once",
    `Best macro-F1: ${short(best.model)} (${f2(best.macro_f1)} / ${f2(best.accuracy)}%)` +
      (() => { const r = pair(best.model, COMP[1].model, "macro_f1");
        return r && num(r.wilcoxon_p) > 0.05 ? ` — tied with ${short(COMP[1].model)} (${f2(COMP[1].macro_f1)})` : ""; })(),
    `Best accuracy: ${short(bestAcc.model)} (${f2(bestAcc.accuracy)}%)`,
    `Plain stacking reaches ${f2(stack4.accuracy)}% accuracy but drops to ${f2(stack4.macro_f1)} macro-F1 — the learned combiner relearns the majority bias`,
  ], { x: 9.2, y: 1.9, w: 3.5, fontSize: 11.5, lineSpacing: 15 });

  s.addNotes(
    "Every model I trained is a point on this chart. Further right is better accuracy, which mostly means getting " +
    "classes 5 and 6 right. Further up is better macro-F1, which treats all six classes equally. The dashed line is " +
    "the frontier — the models that no other model beats on both measures at once. The key message is that there is " +
    "no single best model: moving up costs some rightward position. That is why I fixed macro-F1 as the primary " +
    "metric in advance, and why I report the best model on each axis. One interesting failure: plain stacking gets " +
    "high accuracy but low macro-F1, because the learned combiner relearns the majority-class bias.");
}

// =========================================================================
// 10 — REVIEW 1 vs REVIEW 2
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Review 1 → Review 2", `Best model on the primary metric: ${short(BEST_NAME)}`);

  const mf = headRow("macro_f1"), ba = headRow("balanced_accuracy"), acc = headRow("accuracy");
  statCard(s, 0.6, 1.6, 3.9, f2(mf.review1_ensemble) + " → " + f2(mf.review2_best), "MACRO-F1 (PRIMARY)", BERRY);
  statCard(s, 4.7, 1.6, 3.9, f2(ba.review1_ensemble) + " → " + f2(ba.review2_best), "BALANCED ACCURACY", BERRY);
  statCard(s, 8.8, 1.6, 3.9, f2(acc.review1_ensemble) + " → " + f2(acc.review2_best), "ACCURACY", num(acc.change_vs_review1_ensemble) >= 0 ? BERRY : ROSE);

  const metrics = [["accuracy", "Accuracy"], ["balanced_accuracy", "Balanced accuracy"], ["macro_f1", "Macro-F1"],
    ["recall_3", "Recall, class 3"], ["recall_4", "Recall, class 4"], ["recall_5", "Recall, class 5"],
    ["recall_6", "Recall, class 6"], ["recall_7", "Recall, class 7"], ["recall_8", "Recall, class 8"]];
  tableOn(s, [
    hrow(["Metric (%)", "Review-1 ensemble", "Review-1 Random Forest", "Review-2 best", "Change"]),
    ...metrics.map(([k, lab]) => {
      const r = headRow(k);
      const cells = [lab, f2(r.review1_ensemble), f2(r.review1_random_forest), f2(r.review2_best), signed(r.change_vs_review1_ensemble)];
      return k === "macro_f1" ? boldRow(cells) : cells;
    }),
  ], { x: 0.6, y: 3.25, w: 8.3, colW: [2.2, 1.6, 1.8, 1.5, 1.2], fontSize: 11 });

  const pBest = pair(BEST_NAME, R1_ENS_NAME, "macro_f1");
  text(s,
    `Consistent across repeats: higher macro-F1 than the Review-1 ensemble in ${wins(pBest)} repeats ` +
    `(mean ${signed(pBest.mean_difference)} points; Wilcoxon p ${pfmt(pBest.wilcoxon_p)} — indicative, as repeats share the same wines).`,
    0.6, 6.55, 8.3, 0.6, { fontSize: 11.5, bold: true, color: BERRY, lineSpacing: 15 });

  card(s, 9.2, 3.25, 3.5, 3.0, PALE);
  text(s, "If the goal is accuracy", 9.45, 3.4, 3.1, 0.35, { fontFace: HEADF, fontSize: 14, bold: true, color: BERRY });
  text(s,
    `The best-accuracy model is ${short(bestAcc.model)} at ${f2(bestAcc.accuracy)}% — ` +
    `${signed(num(bestAcc.accuracy) - num(r1Ens.accuracy))} over the Review-1 ensemble. ` +
    `The learned-temperature ensemble gives ${f2(ltR1.accuracy)}% with the paper's own members. ` +
    "Neither comes near the paper's 89.73% — consistent with the Review-1 finding.",
    9.45, 3.8, 3.1, 2.4, { fontSize: 11.5, lineSpacing: 15 });

  s.addNotes(
    `On the primary metric, macro-F1 rises from ${f2(mf.review1_ensemble)} to ${f2(mf.review2_best)}, and balanced ` +
    `accuracy from ${f2(ba.review1_ensemble)} to ${f2(ba.review2_best)}. The table shows where that comes from: ` +
    `the rare classes gain recall, the two common classes give some up, and accuracy moves by ` +
    `${signed(acc.change_vs_review1_ensemble)} points. If the panel cares most about accuracy, the box on the right ` +
    `gives the best accuracy figure instead. Either way, nothing approaches the paper's 89.73 percent, which is ` +
    "consistent with what I showed at Review 1.");
}

// =========================================================================
// 11 — FEATURE IMPORTANCE: METHOD
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Feature importance — three views, checked against each other",
    "No single importance measure is trustworthy alone");

  const views = [
    ["Permutation importance", "PRIMARY", "Shuffle one lab measurement in the held-out test fold and measure how much macro-F1 falls. Model-agnostic, and computed on data the model never trained on — so it measures what the model actually relies on."],
    ["Impurity importance (MDI)", "COMPARISON", "Comes free with Random Forest, but is known to favour continuous, many-valued features. Shown only to check the primary measure."],
    ["Direction of effect", "CONTEXT", "Spearman correlation of each feature with quality. Importance says how much a feature matters; this says which way it pushes."],
  ];
  views.forEach(([h, tag, body], i) => {
    const y = 1.6 + i * 1.2;
    numCircle(s, 0.6, y + 0.05, i + 1, i === 0 ? BERRY : ROSE);
    text(s, h, 1.2, y, 5.5, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
    text(s, tag, 6.8, y + 0.05, 1.6, 0.3, { fontSize: 10.5, bold: true, color: i === 0 ? BERRY : MUTED });
    text(s, body, 1.2, y + 0.38, 11.4, 0.8, { fontSize: 12.5, lineSpacing: 16 });
  });

  card(s, 0.6, 5.3, 12.1, 0.95, PALE);
  text(s,
    "Then a practical test: retrain with only the top-k measurements, chosen inside each training fold. Choosing them " +
    "on the full dataset first would leak test information into the choice.",
    0.9, 5.42, 11.5, 0.75, { fontSize: 12.5, color: BERRY, lineSpacing: 17 });

  s.addNotes(
    "For feature importance I used three methods and checked them against each other. The primary one is permutation " +
    "importance: shuffle a single lab measurement in the test fold — which breaks its link to quality — and see how " +
    "much the score drops. Because it is computed on held-out data, it measures what the model really uses. Random " +
    "Forest's built-in importance is shown for comparison only, because it is biased towards continuous features. " +
    "The third view is direction: does a higher value mean better or worse wine. Finally I tested how many " +
    "measurements are actually needed, with the selection done inside each fold to avoid leakage.");
}

// =========================================================================
// 12 — FEATURE IMPORTANCE: WHAT DRIVES QUALITY
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "What drives the prediction", "Permutation importance on held-out folds — gold bars are the attributes Ma et al. highlight");
  image(s, FIG("C1_permutation_importance.png"), 0.6, 1.45, 12.1, 4.84);

  const missing = crossOut.map((r) => `${r.paper_attribute} ranks #${r.our_rank_best_model}`).join("; ");
  text(s,
    `Top four: ${fiTop.join(", ")}. ${crossIn.length} of the paper's 4 key attributes are in our top four` +
    (crossOut.length ? ` — ${missing}.` : "."),
    0.6, 6.4, 12.1, 0.7, { fontSize: 13, bold: true, color: BERRY, lineSpacing: 17 });

  s.addNotes(
    `The left panel is the best Review-2 model, the right is Random Forest. Longer bars mean the score falls more ` +
    `when that measurement is scrambled. Our top four are ${fiTop.join(", ")}. The gold bars are the four attributes ` +
    `the paper singles out, and ${crossIn.length} of them land in our top four` +
    (crossOut.length ? `; ${missing}, so I only partly confirm the paper on that point.` : ".") +
    " Features with a bar at or below zero carry no usable signal for that model: shuffling them does not hurt.");
}

// =========================================================================
// 13 — DIRECTION AND AGREEMENT
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Do the methods agree — and which way does each feature push?", "");
  image(s, FIG("C2_importance_methods_and_direction.png"), 0.6, 1.2, 12.1, 4.84);

  const ag = AGREE.map((r) => num(r.spearman_rank_agreement));
  const pos = FI.filter((r) => num(r.spearman_rho) > 0.2).map((r) => r.feature);
  const neg = FI.filter((r) => num(r.spearman_rho) < -0.2).map((r) => r.feature);
  bullets(s, [
    `Rank agreement between the three methods: ${Math.min(...ag).toFixed(2)} – ${Math.max(...ag).toFixed(2)} (1 = identical order) — the ranking is not an artefact of one method`,
    `Better wine: higher ${pos.join(", ")}.  Worse wine: higher ${neg.join(", ")}.`,
  ], { y: 6.1, w: 12.1, fontSize: 12.5, lineSpacing: 16 });

  s.addNotes(
    "On the left, three importance measures side by side, each as a share of the total. They broadly agree — the " +
    `rank correlations between them run from ${Math.min(...ag).toFixed(2)} to ${Math.max(...ag).toFixed(2)} — so the ` +
    "ranking is not an artefact of one method. On the right is direction. Higher alcohol and sulphates go with " +
    "better wine; higher volatile acidity — essentially a vinegar note — goes with worse wine. That matches basic " +
    "wine chemistry, which is a useful sanity check that the model is learning something real.");
}

// =========================================================================
// 14 — HOW MANY LAB TESTS ARE NEEDED
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "How many lab tests does the model need?", "Random Forest, class-weighted; features chosen inside each training fold");
  image(s, FIG("C3_feature_subset.png"), 0.6, 1.45, 7.6, 4.22);

  const keep = (100 * num(top4.accuracy) / num(full11.accuracy)).toFixed(0);
  text(s, "Business reading", 8.5, 1.5, 4.2, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    `4 tests (${top4.features_most_often_chosen}) reach ${f2(top4.accuracy)}% accuracy — ${keep}% of what all 11 achieve (${f2(full11.accuracy)}%)`,
    `Macro-F1 with 4 tests: ${f2(top4.macro_f1)} vs ${f2(full11.macro_f1)} with all 11`,
    `The paper's own 4 attributes: ${f2(paper4.accuracy)}% — ${num(paper4.accuracy) < num(top4.accuracy) ? "below" : "above"} our data-chosen four`,
    "A winery screening batches could run a much smaller test panel for most of the predictive value",
  ], { x: 8.5, y: 1.95, w: 4.2, fontSize: 12.5, lineSpacing: 17 });

  s.addNotes(
    "This is the practical side of feature importance. I retrained using only the top k measurements, chosen inside " +
    `each fold. With four tests the model reaches ${f2(top4.accuracy)} percent accuracy, against ${f2(full11.accuracy)} ` +
    `with all eleven — about ${keep} percent of the value. The four the paper highlights reach ${f2(paper4.accuracy)} ` +
    "percent, so a data-driven choice of four does at least as well. For the business setting in the paper's title, " +
    "that suggests a cheaper test panel for routine screening.");
}

// =========================================================================
// 15 — CONCLUSION
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Conclusion", { x: 0.6, y: 0.4, w: 12.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 32, bold: true, color: WHITE });

  const items = [
    ["Class balancing", `Done. ${LABEL[bestBalancing]} lifts macro-F1 from ${f2(r1Ens.macro_f1)} to ${f2(ens(bestBalancing).macro_f1)} and rare-class recall sharply, at a stated cost in accuracy.`],
    ["Improving the result", `The Review-1 diagnosis was tested and confirmed, then fixed: a temperature learned inside each fold takes the paper's own ensemble from ${f2(r1Ens.accuracy)}% to ${f2(ltR1.accuracy)}%. Best macro-F1 overall: ${f2(best.macro_f1)}.`],
    ["Feature importance", `${cap(fiTop.slice(0, 3).join(", "))} drive the prediction; three methods agree; ${crossIn.length} of the paper's 4 key attributes confirmed. Four lab tests carry most of the value.`],
  ];
  items.forEach(([h, b], i) => {
    const y = 1.35 + i * 1.25;
    s.addText(h, { x: 0.6, y, w: 3.2, h: 0.4, isTextBox: true, margin: 0, fontFace: HEADF, fontSize: 17, bold: true, color: GOLD });
    s.addText(b, { x: 3.9, y, w: 8.8, h: 1.1, isTextBox: true, margin: 0, valign: "top", fontFace: BODY, fontSize: 13.5, color: WHITE, lineSpacing: 18 });
  });

  s.addText("What did not change", { x: 0.6, y: 5.25, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 16, bold: true, color: GOLD });
  s.addText(
    `No configuration comes near the paper's 89.73% — the best accuracy here is ${f2(bestAcc.accuracy)}%. Review 2 ` +
    "strengthens the Review-1 conclusion rather than overturning it.",
    { x: 0.6, y: 5.7, w: 12.1, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: "F0E4E8", lineSpacing: 18 });

  s.addNotes(
    "To summarise all three requests. Class balancing is done, and it does what it should: the rare classes are no " +
    "longer ignored, at a cost I have stated. On improving the result, I tested my own Review-1 explanation, it held, " +
    "and the fix — learning the temperature inside each fold — improves the paper's own ensemble without touching " +
    `the test data. On feature importance, ${fiTop[0]}, ${fiTop[1]} and ${fiTop[2]} drive the prediction, three ` +
    "different methods agree on that, and a handful of lab tests carry most of the value. And finally, none of this " +
    "gets anywhere near the paper's 89.73 percent, which supports the Review-1 conclusion.");
}

// =========================================================================
// 16 — LIMITATIONS, FUTURE WORK, REFERENCES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Limitations, future work and references", "");

  text(s, "Limitations", 0.6, 1.3, 6.2, 0.35, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
  bullets(s, [
    "The best model is chosen on the same CV that scores it — a small optimistic bias",
    "The 10 repeats reuse the same wines, so the paired test across them is indicative, not a formal confidence interval",
    "Class 3 has 10 wines in total; no method can learn it reliably from that",
    "Untuned hyperparameters throughout — kept fixed so comparisons stay fair",
  ], { x: 0.6, y: 1.7, w: 6.2, fontSize: 12, lineSpacing: 16 });

  text(s, "Future work", 0.6, 4.0, 6.2, 0.35, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
  bullets(s, [
    "Nested CV around the model choice itself, and a corrected resampled t-test for proper confidence intervals",
    "Ordinal models that know a 7 is closer to an 8 than to a 3",
    "Repeat everything on the 4,898-sample white wine set",
  ], { x: 0.6, y: 4.4, w: 6.2, fontSize: 12, lineSpacing: 16 });

  text(s, "References", 7.2, 1.3, 5.5, 0.35, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
  s.addText([
    { text: "[1]  Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to table: Uncovering wine quality for sales management through machine learning. Journal of Business Research, 176, 114576.", options: { breakLine: true } },
    { text: "[2]  Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. Decision Support Systems, 47(4), 547–553.", options: { breakLine: true } },
    { text: "[3]  Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. Journal of Artificial Intelligence Research, 16, 321–357.", options: { breakLine: true } },
    { text: "[4]  Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.", options: { breakLine: true } },
    { text: "[5]  Wolpert, D. H. (1992). Stacked generalization. Neural Networks, 5(2), 241–259.", options: { breakLine: true } },
    { text: "[6]  Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. JMLR, 12, 2825–2830.", options: { breakLine: true } },
    { text: "[7]  UCI Machine Learning Repository — Wine Quality Dataset.", options: {} },
  ], { x: 7.2, y: 1.7, w: 5.5, h: 4.5, isTextBox: true, margin: 0, valign: "top",
    fontFace: BODY, fontSize: 10.5, color: INK, paraSpaceAfter: 8, lineSpacing: 14 });

  s.addText("Thank you — questions welcome.", { x: 0.6, y: 6.4, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });

  s.addNotes(
    "Four honest limitations. The most important is the first: I pick the best model on the same cross-validation that " +
    "scores it, which flatters it slightly — nested cross-validation around the choice itself would remove that, and " +
    "it is my first item of future work. Second, I report point estimates, not confidence intervals. Third, class 3 " +
    "has only ten wines, which no method can learn reliably. Thank you — I am happy to take questions.");
}

// =========================================================================
// BACKUP SLIDES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Backup 1 — every candidate, ranked by macro-F1", "Pooled over 100 fold-runs");
  const top = COMP.slice(0, 14);
  tableOn(s, [
    hrow(["#", "Model", "Kind", "Accuracy", "Bal. acc.", "Macro-F1"]),
    ...top.map((r) => [r.rank_by_macro_f1, short(r.model), r.kind, f2(r.accuracy), f2(r.balanced_accuracy), f2(r.macro_f1)]),
  ], { y: 1.5, colW: [0.5, 6.4, 1.6, 1.2, 1.2, 1.2], fontSize: 10.5 });
  text(s, `Showing the top ${top.length} of ${COMP.length}. Full table: results/review2/tables/model_comparison.csv`,
    0.6, 6.7, 12.1, 0.35, { fontSize: 11, color: MUTED });
  s.addNotes("Pull this out if asked for the full ranking or for a specific model's numbers.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 2 — confusion matrices, Review 1 vs Review 2", "Pooled over 100 fold-runs (15,990 predictions); rows = true class");
  const cmRows = (cm) => [hrow(["true \\ pred", "3", "4", "5", "6", "7", "8"]),
    ...cm.map((r) => [r[""].replace("true_", ""), r.pred_3, r.pred_4, r.pred_5, r.pred_6, r.pred_7, r.pred_8])];
  text(s, "Review-1 ensemble", 0.6, 1.5, 5.9, 0.3, { fontFace: HEADF, fontSize: 14, bold: true, color: BERRY });
  tableOn(s, cmRows(CM1), { x: 0.6, y: 1.85, w: 5.9, colW: [1.15, 0.79, 0.79, 0.79, 0.79, 0.79, 0.8], fontSize: 11 });
  text(s, "Review-2 best: " + short(BEST_NAME), 6.8, 1.5, 5.9, 0.3, { fontFace: HEADF, fontSize: 14, bold: true, color: BERRY });
  tableOn(s, cmRows(CM2), { x: 6.8, y: 1.85, w: 5.9, colW: [1.15, 0.79, 0.79, 0.79, 0.79, 0.79, 0.8], fontSize: 11 });
  text(s, "The diagonal is correct predictions. Balancing moves predictions off the 5/6 columns into the rare classes — " +
    "more rare wines caught, and some common wines now mislabelled as rare.",
    0.6, 5.3, 12.1, 0.8, { fontSize: 12, color: MUTED, lineSpacing: 17 });
  s.addNotes("Pull this out if asked to show exactly where the predictions moved.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 3 — weight-sharpening sweep (diagnostic)", "Review-1 members; ensemble accuracy and largest average weight at each temperature");
  tableOn(s, [
    hrow(["T", "Accuracy — accuracy term only", "Largest weight", "Accuracy — both terms", "Largest weight"]),
    ...sweepAcc.map((r, i) => [String(r.T), r.acc.toFixed(2), r.w.toFixed(3), sweepBoth[i].acc.toFixed(2), sweepBoth[i].w.toFixed(3)]),
  ], { y: 1.6, colW: [1.2, 3.3, 2.0, 3.3, 2.3], fontSize: 12 });
  text(s, `Random Forest alone: ${rfAcc.toFixed(2)}%. T = 1 is the paper's own scheme. Never used to pick the final model — ` +
    "the weights here are computed from the predictions they are scored on.", 0.6, 5.0, 12.1, 0.8, { fontSize: 12, color: MUTED, lineSpacing: 17 });
  s.addNotes("Pull this out if asked for the exact numbers behind the sharpening chart.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 4 — feature-importance table", "Percentage points of macro-F1 lost when the feature is shuffled; Spearman ρ with quality");
  tableOn(s, [
    hrow(["Rank", "Feature", "Best model", "Random Forest", "RF impurity", "ρ with quality", "Paper key?"]),
    ...FI.map((r) => [r.rank_final, r.feature, f2(r.final_f1_drop), f2(r.rf_f1_drop), num(r.rf_mdi).toFixed(3),
      num(r.spearman_rho).toFixed(2), r.highlighted_by_paper === "True" ? "yes" : ""]),
  ], { y: 1.5, colW: [0.8, 2.9, 1.7, 1.8, 1.7, 1.9, 1.3], fontSize: 11 });
  s.addNotes("Pull this out if asked for the exact importance values.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 5 — is the improvement consistent?", "Paired comparison across the 10 repeats — every model scored on identical folds");
  tableOn(s, [
    hrow(["Model", "Compared with", "Metric", "Mean diff.", "Repeats won", "Wilcoxon p"]),
    ...PAIRED.map((r) => [short(r.model), short(r.compared_with), r.metric === "macro_f1" ? "Macro-F1" : "Accuracy",
      signed(r.mean_difference), `${r.repeats_won} / ${r.repeats}`, isNaN(num(r.wilcoxon_p)) ? "—" : pfmt(r.wilcoxon_p)]),
  ], { y: 1.5, colW: [3.6, 3.3, 1.2, 1.3, 1.4, 1.3], fontSize: 10.5 });
  text(s, "Caveat: the repeats reuse the same 1,599 wines with different splits, so they are not independent samples and the " +
    "p-values are optimistic. The win count is the plainer evidence.", 0.6, 6.45, 12.1, 0.6, { fontSize: 11.5, color: MUTED, lineSpacing: 15 });
  s.addNotes("Pull this out if asked whether the improvement is statistically meaningful or just noise.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 6 — the Review-1 finding, for reference", "Why the paper's 89.73% does not reproduce — three checks from its own tables");
  const checks = [
    ["Protocol mismatch", "The paper's Table 9 confusion matrix sums to 491 samples — 30.7% of 1,599 — a single hold-out split, not the 100-run CV the text describes."],
    ["Internal arithmetic", "The diagonal of that table is 403 of 491 = 82.08%, 7.65 points below the 89.73% stated in the text."],
    ["Flat weights", "Table 8's weights are never more than 0.053 from 0.25; applied to the paper's own base accuracies they give 67.52%."],
  ];
  checks.forEach(([h, b], i) => {
    const x = 0.6 + i * 4.1;
    numCircle(s, x, 1.65, i + 1);
    text(s, h, x + 0.55, 1.67, 3.4, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
    text(s, b, x + 0.55, 2.08, 3.4, 1.8, { fontSize: 12, lineSpacing: 17 });
  });
  card(s, 0.6, 4.3, 12.1, 1.0, "FBF7F8", ROSE);
  text(s, "Caveat: the Table 9 cells were transcribed by eye from the printed PDF. Reported as \"we could not reconcile " +
    "these figures\" — not as a claim that the paper is wrong.", 0.9, 4.45, 11.5, 0.8, { fontSize: 12.5, color: BERRY, lineSpacing: 17 });
  s.addNotes("Pull this out if a panel member was not at Review 1 and asks why the paper's number is not reproduced.");
}

pres.writeFile({ fileName: OUT }).then((f) => console.log("wrote " + f));
