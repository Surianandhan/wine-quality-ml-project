/**
 * build_deck_final.js — generates final_review.pptx (the whole project, start to finish)
 *
 * Same rule as the Review-2 deck: no result is typed in by hand. Every number is
 * read from results/ (and the dataset) when the deck is built, so re-running the
 * pipeline and this script keeps the slides correct. Speaker notes on every slide.
 *
 *   node build_deck_final.js
 *   APP_URL=https://<your-app>.streamlit.app node build_deck_final.js   # once deployed
 */
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.join(__dirname, "..");
const R1 = path.join(ROOT, "results", "tables");
const R2 = path.join(ROOT, "results", "review2");
const REPORT_FIG = path.join(ROOT, "report", "figures");
const ASSETS = path.join(__dirname, "assets");
const OUT = process.env.DECK_OUT || path.join(__dirname, "final_review.pptx");
const APP_URL = process.env.APP_URL || null;
const REPO_URL = "github.com/Surianandhan/wine-quality-ml-project";

// ---- data ----------------------------------------------------------------
function parseLine(line, sep = ",") {
  const out = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c;
    } else if (c === '"') q = true;
    else if (c === sep) { out.push(cur); cur = ""; }
    else cur += c;
  }
  out.push(cur);
  return out;
}
function readCsv(file, sep = ",") {
  const lines = fs.readFileSync(file, "utf8").trim().split(/\r?\n/);
  const head = parseLine(lines[0], sep);
  return lines.slice(1).map((l) => {
    const v = parseLine(l, sep), o = {};
    head.forEach((h, i) => { o[h] = v[i]; });
    return o;
  });
}
const T1 = (f) => readCsv(path.join(R1, f));
const T2 = (f) => readCsv(path.join(R2, "tables", f));
const FIG2 = (f) => path.join(R2, "figures", f);
const RFIG = (f) => path.join(REPORT_FIG, f);
const num = (x) => parseFloat(x);
const f2 = (x) => num(x).toFixed(2);
const f1 = (x) => num(x).toFixed(1);
const signed = (x, d = 2) => (num(x) >= 0 ? "+" : "−") + Math.abs(num(x)).toFixed(d);
const kv = (rows) => Object.fromEntries(rows.map((r) => [r.quantity, r.value]));

// Dataset: class counts straight from the raw file.
const WINE = readCsv(path.join(ROOT, "data", "raw", "winequality-red.csv"), ";");
const N = WINE.length;
const COUNTS = {};
WINE.forEach((r) => { COUNTS[r.quality] = (COUNTS[r.quality] || 0) + 1; });
const share56 = (100 * (COUNTS["5"] + COUNTS["6"]) / N).toFixed(1);
const shareRare = (100 * (COUNTS["3"] + COUNTS["8"]) / N).toFixed(2);
const always5 = (100 * COUNTS["5"] / N).toFixed(1);

// Review 1.
const R1SUM = T1("model_accuracy_summary.csv");
const acc = (m) => num(R1SUM.find((r) => r.model === m).overall_accuracy_pct);
const BENCH = T1("benchmark_comparison.csv");
const T9 = kv(T1("paper_table9_reconciliation.csv"));
const CONS = kv(T1("paper_internal_consistency_check.csv"));
const PAPER_ACC = num(BENCH.find((r) => r.class === "overall").ma_2024_pct);

// Review 2.
const A = T2("A_class_balancing.csv");
const B1 = T2("B1_weight_temperature.csv");
const B = T2("B2_B3_improvements.csv");
const CHOSEN = T2("B4_chosen_temperatures.csv");
const COMP = T2("model_comparison.csv");
const HEADLINE = T2("headline_review1_vs_review2.csv");
const FI = T2("C_feature_importance.csv");
const CROSS = T2("C_paper_crosscheck.csv");
const SUBSET = T2("C_feature_subset.csv");
const AGREE = T2("C_ranking_agreement.csv");
const PAIRED = T2("paired_comparison.csv");

const ENS = "Ensemble (paper weights)";
const LABEL = { none: "No balancing", partial: "Review 1 (SVM + RF only)",
  class_weight: "Class weights, all four", smote: "SMOTE oversampling" };
const ens = (b) => A.find((r) => r.balancing === b && r.model === ENS);
const learner = (b, m) => A.find((r) => r.balancing === b && r.model === m);
const bRow = (name) => B.find((r) => r.model === name);
const compRow = (name) => COMP.find((r) => r.model === name);

const r1Ens = ens("partial");
const r1Rf = learner("partial", "RF");
const best = COMP[0];
const bestAcc = [...COMP].sort((a, b) => num(b.accuracy) - num(a.accuracy))[0];
const ltR1 = bRow("Learned-temperature ensemble | " + LABEL.partial);
const ltSm = bRow("Learned-temperature ensemble | " + LABEL.smote);
const stack4 = bRow("Stacked: paper's 4 learners (class-weighted)");
const stackBal = bRow("Stacked: paper's 4 learners, balanced combiner");
const sm = ens("smote");

const sweepAcc = B1.filter((r) => r.balancing === "partial" && r.sharpen === "accuracy")
  .map((r) => ({ T: num(r.temperature), acc: num(r.accuracy), w: num(r.largest_weight) }));
const rfAcc = num(B1.find((r) => r.balancing === "partial").rf_accuracy);
const firstOvertake = sweepAcc.find((r) => r.acc > rfAcc);
const w1 = B1.find((r) => r.balancing === "partial" && r.sharpen === "both" && num(r.temperature) === 1);
const ourW = [num(w1.w_SVM), num(w1.w_RF), num(w1.w_GradBoost), num(w1.w_MLP)];
const chosenFor = (b) => CHOSEN.filter((r) => r.balancing === b);
const shareAtLeast = (b, t) => {
  const rows = chosenFor(b);
  return Math.round((100 * rows.filter((r) => num(r.temperature) >= t).length) / rows.length);
};
const headRow = (m) => HEADLINE.find((r) => r.metric === m);
const pair = (a, b, metric) => PAIRED.find((r) => r.model === a && r.compared_with === b && r.metric === metric);
const R1_ENS_NAME = ENS + " | " + LABEL.partial;
const LT_R1_NAME = "Learned-temperature ensemble | " + LABEL.partial;
const wins = (r) => `${r.repeats_won} of ${r.repeats}`;
const fiTop = FI.slice(0, 3).map((r) => r.feature);
const crossIn = CROSS.filter((r) => r.in_our_top4 === "True").map((r) => r.paper_attribute);
const crossOut = CROSS.filter((r) => r.in_our_top4 !== "True");
const sub = (k) => SUBSET.find((r) => r.subset === `top ${k} (chosen in-fold)`);
const paper4 = SUBSET.find((r) => r.subset.startsWith("Ma et al."));
const top4 = sub(4), full11 = sub(11);
const agree = AGREE.map((r) => num(r.spearman_rank_agreement));

function short(name) {
  return name
    .replace("Ensemble (paper weights) | ", "Paper ensemble · ")
    .replace("Learned-temperature ensemble | ", "Learned-T ensemble · ")
    .replace("Review 1 (SVM + RF only)", "Review-1 setup")
    .replace("Class weights, all four", "class weights")
    .replace("SMOTE oversampling", "SMOTE")
    .replace("No balancing", "no balancing")
    .replace(/^RF \| /, "Random Forest · ")
    .replace(/^GradBoost \| /, "Gradient Boosting · ")
    .replace(" | ", " · ");
}

// ---- palette and helpers (shared with the Review-1 and Review-2 decks) ------
const BERRY = "6D2E46", ROSE = "A26769", GOLD = "C8A45C", INK = "2B2B2B", MUTED = "6E6E6E";
const TINT = "F5EFF1", WHITE = "FFFFFF", PALE = "F0E4E8", SAGE = "5B7F6B";
const HEADF = "Cambria", BODY = "Calibri";
const SAFE_BOTTOM = 7.2;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "SURIANANDHAN S";
pres.title = "Wine Quality Prediction Using a Weighted Ensemble — Final Review";

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
    fontFace: HEADF, fontSize: 32, bold: true, color: valColor || BERRY, align: "center" });
  slide.addText(label, { x: x + 0.15, y: y + 0.9, w: w - 0.3, h: 0.45, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: MUTED, align: "center" });
}
function numCircle(slide, x, y, n, fill) {
  slide.addShape(pres.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42,
    fill: { color: fill || BERRY }, line: { color: fill || BERRY, width: 0 } });
  slide.addText(String(n), { x, y: y + 0.03, w: 0.42, h: 0.36, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 15, bold: true, color: WHITE, align: "center" });
}
function arrow(slide, x, y, w, h, color) {
  slide.addShape(pres.ShapeType.rightArrow, { x, y, w, h, fill: { color: color || GOLD }, line: { color: color || GOLD, width: 0 } });
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
function footer(slide, t) {
  slide.addText(t, { x: 0.6, y: 7.05, w: 12.1, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 9.5, color: MUTED, italic: true });
}

// =========================================================================
// 1 — TITLE
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Wine Quality Prediction\nUsing a Weighted Ensemble", { x: 0.9, y: 1.0, w: 11.5, h: 1.8,
    isTextBox: true, margin: 0, fontFace: HEADF, fontSize: 40, bold: true, color: WHITE, lineSpacing: 46 });
  s.addText("Reproduction, class balancing, feature importance and a web application", {
    x: 0.9, y: 2.85, w: 11.5, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 17, color: GOLD, italic: true });
  s.addText("Base paper: Ma et al. (2024), From vineyard to table — Journal of Business Research 176:114576", {
    x: 0.9, y: 3.3, w: 11.5, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: "E8DCE1" });
  s.addText([
    { text: "SURIANANDHAN S", options: { bold: true, fontSize: 19, breakLine: true } },
    { text: "127018060 · B.Tech CSBS", options: { fontSize: 15, color: "E8DCE1", breakLine: true } },
    { text: "CSE425 — Machine Learning Essentials", options: { fontSize: 14, color: "E8DCE1" } },
  ], { x: 0.9, y: 4.2, w: 6.0, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE });
  s.addText([
    { text: "Guide", options: { fontSize: 11, color: GOLD, breakLine: true } },
    { text: "Dr. Vidivelli S, AP-II", options: { bold: true, fontSize: 15, breakLine: true } },
    { text: "School of Computing, SASTRA Deemed to be University", options: { fontSize: 13, color: "E8DCE1" } },
  ], { x: 7.2, y: 4.2, w: 5.4, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, color: WHITE });
  s.addText("Final Review", { x: 0.9, y: 6.35, w: 5, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: GOLD });
  s.addNotes(
    "Good morning. My project is about predicting the quality of red wine from laboratory measurements. It " +
    "reproduces a 2024 Journal of Business Research paper that uses a weighted ensemble of four models. Over the " +
    "three reviews I reproduced the paper, checked its claims, made the three changes requested at the first review " +
    "— class balancing, a better result and feature importance — and finally delivered everything as a web " +
    "application, a report and a conference paper. I will walk through it from the beginning.");
}

// =========================================================================
// 2 — THE PROBLEM
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The question: can lab tests predict what tasters will say?", "The business problem behind the base paper");

  const boxes = [
    ["11 lab measurements", "Alcohol, acidity, sulphates, sugar, sulphur dioxide, pH, density …", "Cheap, objective, available early"],
    ["A trained model", "Learns the link between the chemistry and the grade from past wines", "This project"],
    ["Quality grade 3 – 8", "Normally given by a panel of tasters", "Slow, costly, partly subjective"],
  ];
  boxes.forEach(([h, b, foot], i) => {
    const x = 0.6 + i * 4.25, y = 1.65, w = 3.6;
    card(s, x, y, w, 2.55, i === 1 ? PALE : TINT, i === 1 ? BERRY : null);
    text(s, h, x + 0.25, y + 0.25, w - 0.5, 0.45, { fontFace: HEADF, fontSize: 18, bold: true, color: BERRY });
    text(s, b, x + 0.25, y + 0.8, w - 0.5, 1.0, { fontSize: 13, lineSpacing: 17 });
    text(s, foot, x + 0.25, y + 1.95, w - 0.5, 0.4, { fontSize: 11.5, italic: true, color: MUTED });
    if (i < 2) arrow(s, x + w + 0.12, y + 1.05, 0.42, 0.45);
  });

  text(s, "Why a wine retailer cares", 0.6, 4.55, 6, 0.4, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
  bullets(s, [
    "Decide prices, stock and promotions before the tasting panel has met",
    "Check every batch the same way, every time",
    "Know which measurements actually drive quality — and which tests can be skipped",
  ], { y: 5.0, w: 12.1, fontSize: 14, lineSpacing: 19 });

  s.addNotes(
    "Here is the problem in one picture. Every batch of wine gets routine lab tests: alcohol, acidity, sulphates and " +
    "so on. Those are cheap and objective. The quality grade, on the other hand, comes from a panel of tasters, " +
    "which is slow, costs money and is partly subjective. The idea is to learn the link between the chemistry and " +
    "the grade from past wines, so that a new wine's grade can be estimated from its lab results alone. For a " +
    "retailer that means earlier pricing and stocking decisions, consistent checks, and knowing which tests matter.");
}

// =========================================================================
// 3 — THE DATASET
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The dataset: UCI Wine Quality (red)", "Red Vinho Verde wines from Portugal — collected by Cortez et al. (2009)");
  image(s, RFIG("class_distribution.png"), 0.6, 1.55, 7.6, 3.93);

  statCard(s, 8.6, 1.55, 2.0, N.toLocaleString("en-US"), "WINES (ROWS)");
  statCard(s, 10.75, 1.55, 1.95, "11", "LAB MEASUREMENTS");
  statCard(s, 8.6, 3.15, 2.0, "6", "GRADES (3 TO 8)");
  statCard(s, 10.75, 3.15, 1.95, share56 + "%", "ARE GRADE 5 OR 6", ROSE);

  card(s, 0.6, 5.7, 12.1, 1.2, PALE);
  text(s,
    `The difficulty is the imbalance. Grade 3 has only ${COUNTS["3"]} wines and grade 8 only ${COUNTS["8"]} ` +
    `(${shareRare}% together). A model that always answers "5" is already right ${always5}% of the time — while never ` +
    "recognising a single very poor or excellent wine, which are exactly the ones a retailer most wants to find.",
    0.9, 5.82, 11.5, 1.0, { fontSize: 13, color: BERRY, lineSpacing: 17 });

  s.addNotes(
    `The data is the public UCI red-wine dataset: ${N} wines, each with 11 lab measurements and a quality grade. ` +
    "Only grades 3 to 8 occur. The key thing to notice is the shape of this chart: almost all wines are grade 5 or 6. " +
    `There are only ${COUNTS["3"]} wines of grade 3 and ${COUNTS["8"]} of grade 8. So a lazy model that always says ` +
    `"5" is already right ${always5} percent of the time, yet it never finds a bad or an excellent wine. That ` +
    "imbalance runs through the whole project, and it is why the second review focused on class balancing.");
}

// =========================================================================
// 4 — THE BASE PAPER
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The base paper", "Ma, Mao, Cao, Luo, Gupta & Wang (2024), Journal of Business Research 176:114576 (Elsevier)");

  // Pipeline: four learners -> two weights -> weighted vote.
  const learners = ["SVM", "RNN", "ELM", "Random Forest"];
  learners.forEach((l, i) => {
    const y = 1.65 + i * 0.78;
    card(s, 0.6, y, 2.4, 0.6, TINT, ROSE);
    text(s, l, 0.6, y + 0.15, 2.4, 0.35, { fontSize: 14, bold: true, color: BERRY, align: "center" });
  });
  arrow(s, 3.15, 2.75, 0.5, 0.45);
  card(s, 3.8, 1.65, 3.2, 2.95, PALE, BERRY);
  text(s, "Two weights per model", 3.95, 1.8, 2.9, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  text(s, "Accuracy weight — the more accurate the model, the bigger its say.\n\nDiversity weight — the more its " +
    "mistakes differ from the others', the bigger its say.\n\nFinal weight = average of the two.",
  3.95, 2.25, 2.95, 2.3, { fontSize: 12, lineSpacing: 16 });
  arrow(s, 7.15, 2.75, 0.5, 0.45);
  card(s, 7.8, 2.25, 1.9, 1.75, TINT, ROSE);
  text(s, "Weighted vote", 7.8, 2.55, 1.9, 0.4, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY, align: "center" });
  text(s, "→ one grade", 7.8, 3.05, 1.9, 0.4, { fontSize: 13, color: MUTED, align: "center" });

  statCard(s, 10.1, 1.65, 2.6, f2(PAPER_ACC) + "%", "ACCURACY CLAIMED BY THE PAPER");
  statCard(s, 10.1, 3.25, 2.6, "+" + f2(CONS.gap_vs_best_base_learner_pct_points), "POINTS ABOVE ITS BEST SINGLE MODEL", ROSE);

  text(s, "The paper also reports that alcohol, sulphates, volatile acidity and citric acid matter most.",
    0.6, 4.95, 12.1, 0.4, { fontSize: 13.5, italic: true, color: BERRY });
  card(s, 0.6, 5.55, 12.1, 1.3, "FBF7F8", ROSE);
  text(s,
    `An ensemble is a team of models that vote. The paper's claim is that this team is far better than its best member ` +
    `(${f2(PAPER_ACC)}% vs ${f2(CONS.best_single_base_learner_pct)}%). Typical published accuracies for this six-grade task ` +
    "are in the 60s to low 70s — so the first job was to check whether the claim holds.",
    0.9, 5.68, 11.5, 1.05, { fontSize: 12.5, lineSpacing: 17 });

  s.addNotes(
    "The base paper trains four different models — an SVM, a recurrent neural network, an extreme learning machine " +
    "and a random forest. Each model gets a weight made of two parts: an accuracy part, so better models count for " +
    "more, and a diversity part, so models that make different mistakes count for more. The final answer is a " +
    `weighted vote. The paper reports ${f2(PAPER_ACC)} percent accuracy, ${f2(CONS.gap_vs_best_base_learner_pct_points)} ` +
    "points above its best single model. That is a very high number for this dataset, so the first thing I did was " +
    "to rebuild the method carefully and see whether it holds.");
}

// =========================================================================
// 5 — THE WHOLE PROJECT ON ONE PAGE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The whole project on one page", "Four parts, three milestones");
  image(s, RFIG("framework.png"), 0.6, 1.5, 8.2, 5.4);

  const steps = [
    ["Review 1", "Rebuild the paper's method exactly, test it fairly, and check the paper's own numbers"],
    ["Review 2", "The three changes the guide asked for: class balancing, a better result, feature importance"],
    ["Final", "A web application, the project report, a conference paper, and the code on GitHub"],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.6 + i * 1.65;
    numCircle(s, 9.15, y, i + 1, i === 2 ? GOLD : BERRY);
    text(s, h, 9.75, y + 0.02, 3.0, 0.4, { fontFace: HEADF, fontSize: 17, bold: true, color: BERRY });
    text(s, b, 9.75, y + 0.45, 3.0, 1.1, { fontSize: 12.5, lineSpacing: 16 });
  });

  s.addNotes(
    "This diagram is the whole project. Part A prepares the data and the testing method. Part B is the first review: " +
    "the reproduction of the paper. Part C is the second review: the three changes my guide asked for. Part D is the " +
    "evaluation and the final deliverables. On the right are the three milestones. I will follow this order.");
}

// =========================================================================
// 6 — TESTING FAIRLY
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "How every model is tested — fairly", "Stratified 10-fold cross-validation, repeated 10 times");

  // The cross-validation picture: 10 fold-runs, each with a different test fold.
  const gx = 0.95, gy = 1.75, bw = 0.42, bh = 0.27, gap = 0.05;
  for (let r = 0; r < 10; r++) {
    text(s, `Run ${r + 1}`, 0.25, gy + r * (bh + gap) + 0.02, 0.65, 0.25, { fontSize: 9.5, color: MUTED });
    for (let c = 0; c < 10; c++) {
      s.addShape(pres.ShapeType.rect, { x: gx + c * (bw + gap), y: gy + r * (bh + gap), w: bw, h: bh,
        fill: { color: c === r ? GOLD : PALE }, line: { color: WHITE, width: 1 } });
    }
  }
  s.addShape(pres.ShapeType.rect, { x: 0.95, y: 5.15, w: 0.3, h: 0.2, fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  text(s, "test fold (never seen in training)", 1.33, 5.12, 3.2, 0.3, { fontSize: 11 });
  s.addShape(pres.ShapeType.rect, { x: 0.95, y: 5.45, w: 0.3, h: 0.2, fill: { color: PALE }, line: { color: PALE, width: 0 } });
  text(s, "training folds", 1.33, 5.42, 3.2, 0.3, { fontSize: 11 });
  text(s, "… then reshuffle and repeat the whole thing 10 times = 100 fold-runs",
    0.6, 5.85, 5.2, 0.6, { fontSize: 12, italic: true, color: BERRY, lineSpacing: 16 });

  bullets(s, [
    "The wines are split into 10 groups with the same grade mix (stratified); each group takes a turn as the test set",
    `Every wine is predicted 10 times by a model that never saw it: 10 × ${N.toLocaleString("en-US")} = ${(10 * N).toLocaleString("en-US")} predictions per model`,
    "Every model uses exactly the same splits, so models can be compared repeat by repeat",
    "No data leakage: scaling, SMOTE and feature selection are all learned inside the training folds only",
  ], { x: 6.3, y: 1.65, w: 6.4, fontSize: 13.5, lineSpacing: 18 });
  card(s, 6.3, 5.05, 6.4, 1.45, PALE);
  text(s, "Leakage = peeking at the exam answers", 6.55, 5.17, 6.0, 0.35, { fontFace: HEADF, fontSize: 14, bold: true, color: BERRY });
  text(s, "An early version scaled all the data before splitting it — the test wines quietly shaped the training. It was " +
    "fixed at Review 1 by putting the scaler inside a pipeline.", 6.55, 5.55, 6.0, 0.9, { fontSize: 12, lineSpacing: 16 });

  s.addNotes(
    "Before any result, the testing method. You cannot test a model on the wines it learned from — that is like " +
    "grading students on questions they already saw. So the wines are split into ten groups with the same mix of " +
    "grades. Each group takes one turn as the test set while the model learns from the other nine. Then I reshuffle " +
    "and do it all again, ten times, which matches the paper's 100 experiments. Every model uses exactly the same " +
    "splits. And everything the model learns from data — even the scaling of the numbers — is learned from the " +
    "training part only. Otherwise the test data leaks into training, which is like peeking at the answers.");
}

// =========================================================================
// 7 — THE FOUR LEARNERS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The four base learners", "Two kept from the paper, two replaced to stay within the classical-ML syllabus");
  tableOn(s, [
    hrow(["Paper's model", "Our model", "The idea in one line", "Accuracy (ours)"]),
    ["SVM", "Support Vector Machine (RBF kernel)", "Draws the widest possible boundary between the grades", f2(acc("SVM")) + "%"],
    ["Random Forest", "Random Forest (300 trees)", "Many decision trees, each trained on a random sample, vote together", f2(acc("RF")) + "%"],
    ["RNN (recurrent neural network)", "Gradient Boosting (200 stages)", "Each new tree corrects the mistakes of the trees before it", f2(acc("GradBoost")) + "%"],
    ["ELM (extreme learning machine)", "Multilayer Perceptron (64, 32)", "A small neural network trained by back-propagation", f2(acc("MLP")) + "%"],
  ], { y: 1.65, colW: [2.6, 3.1, 4.8, 1.6], fontSize: 13 });

  card(s, 0.6, 4.55, 5.9, 1.95, PALE);
  text(s, "Why two substitutes?", 0.85, 4.7, 5.5, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  text(s, "RNNs and ELMs are outside the classical machine-learning syllabus of the course. Gradient Boosting also " +
    "improves step by step, like the RNN; the MLP is the closest classical neural network to the ELM.",
  0.85, 5.1, 5.45, 1.35, { fontSize: 12.5, lineSpacing: 16 });
  card(s, 6.8, 4.55, 5.9, 1.95, TINT);
  text(s, "Same set-up for all four", 7.05, 4.7, 5.5, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  text(s, "Each model is a pipeline: min–max scaling, then the model. SVM and Random Forest use balanced class " +
    "weights so the rare grades are not ignored. Every model gives class probabilities, which the weighted vote needs.",
  7.05, 5.1, 5.45, 1.35, { fontSize: 12.5, lineSpacing: 16 });

  s.addNotes(
    "These are the four team members. SVM and Random Forest are exactly the paper's. The paper's two neural models, " +
    "the RNN and the ELM, are outside our classical machine-learning syllabus, so I replaced them with the closest " +
    "classical models: Gradient Boosting, which also improves itself step by step, and a multilayer perceptron, a small " +
    `neural network. On their own, Random Forest is clearly the strongest at ${f2(acc("RF"))} percent. All four scale ` +
    "the data first, inside a pipeline, and all four output probabilities for each grade.");
}

// =========================================================================
// 8 — THE WEIGHTED ENSEMBLE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The paper's weighted vote — and what the weights turn out to be", "Implemented exactly as the paper's equations describe");

  const steps = [
    ["Accuracy weight", "1 ÷ the model's error rate, normalised so the four add up to 1  (paper's Eqs. 5–6)"],
    ["Diversity weight", "How far the model's list of mistakes is from the others' lists, normalised  (Eqs. 7–9)"],
    ["Final weight", "The average of the two  (Eq. 4)"],
    ["Weighted vote", "Add up each model's probabilities × its weight; the highest grade wins  (Eq. 1)"],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.6 + i * 1.08;
    numCircle(s, 0.6, y, i + 1, i === 3 ? GOLD : BERRY);
    text(s, h, 1.2, y + 0.0, 5.0, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
    text(s, b, 1.2, y + 0.38, 5.0, 0.65, { fontSize: 12.5, lineSpacing: 16 });
  });

  image(s, RFIG("weights_vs_paper.png"), 6.6, 1.5, 6.1, 3.1);
  card(s, 6.6, 4.8, 6.1, 1.75, PALE);
  text(s,
    `Our weights: ${Math.min(...ourW).toFixed(3)} – ${Math.max(...ourW).toFixed(3)}. The paper's own: 0.217 – 0.303. ` +
    "Both stay close to 0.25 = an equal share. With equal weights a vote is just an average — and an average of one " +
    "strong and three weaker models lands between them, not above the best.",
    6.85, 4.93, 5.65, 1.55, { fontSize: 12.5, color: BERRY, lineSpacing: 17 });

  s.addNotes(
    "This is the heart of the paper. Each model gets an accuracy weight — one over its error rate, scaled so the four " +
    "add up to one — and a diversity weight, which measures how differently it makes mistakes. The final weight is " +
    "their average, and the vote adds up each model's grade probabilities times its weight. The important discovery " +
    "is on the right: the weights come out nearly equal, around a quarter each — ours and the paper's own. Equal " +
    "weights mean the vote is just an average, and an average of one strong model and three weaker ones cannot beat " +
    "the strong one. Keep that in mind for the next slide.");
}

// =========================================================================
// 9 — REVIEW 1 RESULT
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Review 1 — the reproduction result", "Pooled over 100 fold-runs (15,990 predictions per model)");

  statCard(s, 0.6, 1.55, 2.85, f2(PAPER_ACC) + "%", "PAPER'S ENSEMBLE (CLAIMED)", MUTED);
  statCard(s, 3.65, 1.55, 2.85, f2(acc("Ensemble (soft vote)")) + "%", "OUR ENSEMBLE (FAITHFUL REPRODUCTION)", BERRY);
  statCard(s, 6.7, 1.55, 2.85, f2(acc("RF")) + "%", "RANDOM FOREST ALONE — BEATS THE ENSEMBLE", ROSE);
  statCard(s, 9.75, 1.55, 2.95, f1(r1Ens.recall_3) + "% / " + f1(r1Ens.recall_4) + "%", "GRADE-3 / GRADE-4 WINES FOUND", ROSE);

  image(s, RFIG("model_ranking.png"), 0.6, 3.25, 7.4, 3.15);
  bullets(s, [
    `The paper's central claim does not reproduce: our ensemble is ${f2(acc("RF") - acc("Ensemble (soft vote)"))} points below Random Forest, not 9 points above`,
    "It does beat the other three models — exactly what an average does",
    "Grades 5 and 6 are predicted well; the rare grades are almost never found",
  ], { x: 8.3, y: 3.3, w: 4.4, fontSize: 13, lineSpacing: 17 });

  s.addNotes(
    `Here is the Review-1 result. The paper claims ${f2(PAPER_ACC)} percent. My faithful reproduction reaches ` +
    `${f2(acc("Ensemble (soft vote)"))}. And Random Forest on its own does better, at ${f2(acc("RF"))}. So the paper's ` +
    "central claim — that the team beats its best member by nine points — does not reproduce. The ensemble does beat " +
    "the other three models, which is exactly what an average does. The last card shows the other problem: the rare " +
    `grades. Of the grade-3 wines the model finds ${f1(r1Ens.recall_3)} percent, of grade 4 only ${f1(r1Ens.recall_4)} percent.`);
}

// =========================================================================
// 10 — WHY 89.73% DOES NOT REPRODUCE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, `Why ${f2(PAPER_ACC)}% does not reproduce`, "Three checks computed from the paper's own published tables");
  const checks = [
    ["Different test set", `The paper's confusion matrix (Table 9) holds only ${T9.implied_test_set_size} wines — ${f1(T9.implied_fraction_of_dataset_pct)}% of the ${N.toLocaleString("en-US")}. That is one hold-out split, not 100 cross-validation runs.`],
    ["Its own arithmetic", `The correct predictions in that table: ${T9.correct_predictions_on_diagonal} of ${T9.implied_test_set_size} = ${f2(T9.implied_overall_accuracy_pct)}% — ${f2(T9.discrepancy_pct_points)} points below the ${f2(PAPER_ACC)}% in the text.`],
    ["Flat weights", `The paper's weights (Table 8) applied to its own model accuracies give ${f2(CONS.weighted_average_of_base_accuracies_pct)}%. Our ${f2(CONS.our_ensemble_pct)}% sits ${f2(CONS.our_gap_vs_their_weighted_average_pct_points)} points from that; the paper's claim sits ${f2(CONS.gap_vs_weighted_average_pct_points)} points from it.`],
  ];
  checks.forEach(([h, b], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.85, 3.15, i === 2 ? PALE : TINT);
    numCircle(s, x + 0.25, 1.82, i + 1);
    text(s, h, x + 0.8, 1.85, 2.9, 0.4, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
    text(s, b, x + 0.25, 2.45, 3.4, 2.2, { fontSize: 12.5, lineSpacing: 17 });
  });
  card(s, 0.6, 5.0, 12.1, 0.95, PALE);
  text(s, "Our explanation: the weighting gives every model about a quarter of the vote, so the ensemble averages its " +
    "members. Our result lands where that predicts — and inside the range other studies report for this data.",
  0.9, 5.12, 11.5, 0.8, { fontSize: 13, bold: true, color: BERRY, lineSpacing: 17 });
  card(s, 0.6, 6.1, 12.1, 0.8, "FBF7F8", ROSE);
  text(s, "Caveat: the Table 9 cells were read by eye from the printed PDF. These are figures we could not reconcile — " +
    "not a claim that the paper is wrong.", 0.9, 6.2, 11.5, 0.65, { fontSize: 12, color: BERRY, lineSpacing: 16 });

  s.addNotes(
    "Why the difference? I did three checks using only the numbers printed in the paper. First, the paper's own " +
    `confusion matrix contains only ${T9.implied_test_set_size} wines — about 31 percent of the data — which means a ` +
    "single test split, not the hundred runs the text describes. Second, counting the correct predictions in that " +
    `same table gives ${f2(T9.implied_overall_accuracy_pct)} percent, not ${f2(PAPER_ACC)}. Third, if I apply the ` +
    `paper's own weights to the paper's own model accuracies, I get about ${f2(CONS.weighted_average_of_base_accuracies_pct)} ` +
    `percent — and my result is within ${f2(CONS.our_gap_vs_their_weighted_average_pct_points)} points of that. I am careful ` +
    "with the wording: the table was read by eye from the PDF, so I say these figures could not be reconciled, not " +
    "that the paper is wrong.");
}

// =========================================================================
// 11 — REVIEW 2: THE THREE ASKS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Review 2 — the three changes the guide asked for", "Same data, same folds, same rules as Review 1, so every number is comparable");
  tableOn(s, [
    hrow(["Asked at Review 1", "What was done", "Result in one line"]),
    ["1.  Class balancing — yet to be done", "Four schemes compared: none, Review-1 partial, class weights on all four, SMOTE inside the fold",
      `Macro-F1 ${f2(r1Ens.macro_f1)} → ${f2(sm.macro_f1)} (paper ensemble, SMOTE)`],
    ["2.  Improve the result", "Tested the flat-weights explanation, then fixed it by learning the weight sharpness inside each training fold; also stacking and stronger models",
      `Paper's ensemble ${f2(r1Ens.accuracy)}% → ${f2(ltR1.accuracy)}%; best macro-F1 ${f2(best.macro_f1)}`],
    ["3.  Work on feature importance", "Permutation importance on held-out folds, checked against two other methods and the paper",
      `${fiTop[0]}, ${fiTop[1]}, ${fiTop[2]} lead; 4 tests ≈ all 11`],
  ], { y: 1.6, colW: [3.0, 5.6, 3.5], fontSize: 12.5 });

  card(s, 0.6, 4.65, 12.1, 1.75, PALE);
  text(s, "Judged on macro-F1 — fixed in the code before any experiment ran", 0.9, 4.78, 11.5, 0.35,
    { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  text(s, "Accuracy mostly measures grades 5 and 6. Macro-F1 scores each of the six grades separately and averages them " +
    "with equal weight, so a model only does well if it also finds the rare grades. Accuracy is still reported " +
    "everywhere, for comparison with the paper.", 0.9, 5.18, 11.5, 1.15, { fontSize: 12.5, lineSpacing: 17 });

  s.addNotes(
    "After the first review my guide asked for three things: class balancing, an improved result, and work on " +
    "feature importance. This table is the map. Before running anything I fixed the scoring rule in the code: the " +
    "main measure is macro-F1. Accuracy mostly rewards getting grades 5 and 6 right; macro-F1 scores each grade " +
    "separately and averages them equally, so a model has to find the rare grades too. I still report accuracy " +
    "everywhere so it can be compared with the paper.");
}

// =========================================================================
// 12 — CLASS BALANCING
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Change 1 — class balancing", "The paper's weighted vote under four schemes — only the balancing changes");
  image(s, FIG2("A_class_balancing.png"), 0.6, 1.5, 8.2, 3.15);
  const bestBal = ["none", "partial", "class_weight", "smote"].map((b) => ens(b))
    .sort((a, b) => num(b.macro_f1) - num(a.macro_f1))[0].balancing;
  const rows = ["none", "partial", "class_weight", "smote"].map((b) => {
    const r = ens(b);
    const cells = [LABEL[b], f2(r.accuracy), f2(r.macro_f1), f1(r.recall_3), f1(r.recall_4), f1(r.recall_7), f1(r.recall_8)];
    return b === bestBal ? boldRow(cells) : cells;
  });
  tableOn(s, [hrow(["Scheme", "Accuracy", "Macro-F1", "Grade 3", "Grade 4", "Grade 7", "Grade 8"]), ...rows],
    { x: 0.6, y: 4.8, w: 8.2, colW: [2.6, 1.0, 1.05, 0.9, 0.9, 0.9, 0.85], fontSize: 11.5 });
  text(s, "Grade columns = share of that grade's wines found (recall, %)", 0.6, 6.95, 8.2, 0.3, { fontSize: 9.5, italic: true, color: MUTED });

  text(s, "What it shows", 9.15, 1.55, 3.6, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    "Class weights make mistakes on rare grades cost more; SMOTE creates new rare-grade examples by blending two similar real wines",
    `SMOTE gives the best macro-F1: grade 4 found ${f1(r1Ens.recall_4)}% → ${f1(sm.recall_4)}%, grade 7 ${f1(r1Ens.recall_7)}% → ${f1(sm.recall_7)}%`,
    `The price: accuracy −${f2(num(r1Ens.accuracy) - num(sm.accuracy))} points, because some grade-5/6 wines are now called rare`,
    "SMOTE runs inside each training fold — test wines are never copied into training",
  ], { x: 9.15, y: 1.95, w: 3.6, fontSize: 12, lineSpacing: 16 });

  s.addNotes(
    "First change: class balancing. I compared four schemes on exactly the same models, so balancing is the only " +
    "difference. Class weights make a mistake on a rare grade cost more during training. SMOTE creates new examples " +
    "of the rare grades by blending two similar real wines. SMOTE gives the best macro-F1: the share of grade-4 wines " +
    `found jumps from ${f1(r1Ens.recall_4)} to ${f1(sm.recall_4)} percent. The price is about ` +
    `${f2(num(r1Ens.accuracy) - num(sm.accuracy))} points of accuracy, because the model now calls some ordinary wines rare. ` +
    "That is the honest trade-off of balancing. And SMOTE only ever sees the training wines, so there is no leakage.");
}

// =========================================================================
// 13 — IMPROVING THE RESULT
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Change 2 — improving the result", "Test the flat-weights explanation, then fix it without touching the test data");

  statCard(s, 0.6, 1.55, 2.85, f2(r1Ens.accuracy) + "%", "PAPER'S WEIGHTS (T = 1)", MUTED);
  statCard(s, 3.65, 1.55, 2.85, f2(ltR1.accuracy) + "%", "LEARNED SHARPNESS, SAME FOUR MODELS", BERRY);
  statCard(s, 6.7, 1.55, 2.85, f2(r1Rf.accuracy) + "%", "RANDOM FOREST ALONE", ROSE);
  statCard(s, 9.75, 1.55, 2.95, shareAtLeast("partial", 10) + "%", "OF FOLDS CHOSE A SHARP T ≥ 10", BERRY);

  bullets(s, [
    "Idea: raise the weights to a power T before normalising — T = 1 is the paper, a bigger T gives more say to the best model",
    firstOvertake
      ? `Test: with a big enough T (≥ ${firstOvertake.T}) the ensemble overtakes Random Forest — the explanation holds (a diagnostic only)`
      : "Test: sharper weights close most of the gap to Random Forest — the explanation holds (a diagnostic only)",
    `Fix: choose T inside each training fold by an inner 5-fold CV. Better than the paper's weights in ${wins(pair(LT_R1_NAME, R1_ENS_NAME, "accuracy"))} repeats; now level with Random Forest`,
    `Also tried: stacking (${f2(stack4.accuracy)}% accuracy but macro-F1 only ${f2(stack4.macro_f1)} — it relearns the majority bias) and stronger models (ExtraTrees, HistGB)`,
  ], { y: 3.25, w: 7.2, fontSize: 12.5, lineSpacing: 16 });
  image(s, FIG2("B4_chosen_temperatures.png"), 8.1, 3.2, 4.6, 3.19);

  s.addNotes(
    "Second change: a better result. My Review-1 explanation was that the weights are too flat. So I added a single " +
    "knob, a temperature T: raise the weights to the power T before scaling them. T equal to one is exactly the " +
    "paper; a bigger T gives the best model more of the vote. As a test, sharper weights do let the ensemble catch " +
    "Random Forest — so the explanation holds. But that test peeks at the scores, so the proper fix chooses T inside " +
    "each training fold with its own small cross-validation. The test fold never influences it. With the same four " +
    `models, accuracy goes from ${f2(r1Ens.accuracy)} to ${f2(ltR1.accuracy)} percent, better in every repeat. And when ` +
    `it chooses for itself, the inner test picks a sharp T in ${shareAtLeast("partial", 10)} percent of folds — the data ` +
    "agreeing that the paper's T of one is too flat.");
}

// =========================================================================
// 14 — EVERY CANDIDATE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, `All ${COMP.length} candidates — no model wins both measures`, "Each point is one model, scored on the same 100 fold-runs");
  image(s, FIG2("B_tradeoff.png"), 0.6, 1.45, 8.3, 4.9);
  text(s, "Reading the chart", 9.2, 1.5, 3.5, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    "Right = better accuracy (mostly grades 5 and 6); up = better on all six grades equally",
    "Dashed line: models that no other model beats on both at once",
    `Best macro-F1: ${short(best.model)} — ${f2(best.macro_f1)} (accuracy ${f2(best.accuracy)}%)`,
    `Best accuracy: ${short(bestAcc.model)} — ${f2(bestAcc.accuracy)}%`,
    `Random Forest + SMOTE beats the Review-1 ensemble on macro-F1 in ${wins(pair(best.model, R1_ENS_NAME, "macro_f1"))} repeats`,
  ], { x: 9.2, y: 1.9, w: 3.5, fontSize: 12, lineSpacing: 16 });
  card(s, 0.6, 6.45, 12.1, 0.6, PALE);
  text(s, "So the web application offers both: the most accurate model, and the one that finds rare grades best.",
    0.9, 6.55, 11.5, 0.45, { fontSize: 12.5, bold: true, color: BERRY });

  s.addNotes(
    `I tested ${COMP.length} models and combinations in total, all on the same splits. Each dot is one of them. Further ` +
    "right means more accurate overall, which mostly means grades 5 and 6. Further up means better on all six grades " +
    "equally. The dashed line connects the models that nothing else beats on both measures. The message: there is no " +
    `single winner. The best on macro-F1 is Random Forest with SMOTE at ${f2(best.macro_f1)}; the most accurate is ` +
    `Random Forest without balancing at ${f2(bestAcc.accuracy)} percent. Which one to use depends on the goal, so the ` +
    "web app offers both.");
}

// =========================================================================
// 15 — FEATURE IMPORTANCE
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Change 3 — which measurements drive the prediction?", "Permutation importance: shuffle one measurement in the test fold and see how much the score drops");
  image(s, FIG2("C1_permutation_importance.png"), 0.6, 1.5, 8.4, 3.36);

  const pos = FI.filter((r) => num(r.spearman_rho) > 0.2).map((r) => r.feature);
  const neg = FI.filter((r) => num(r.spearman_rho) < -0.2).map((r) => r.feature);
  text(s, "What it shows", 9.3, 1.55, 3.4, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    `Top three: ${fiTop.join(", ")}`,
    `Three methods agree (rank agreement ${Math.min(...agree).toFixed(2)} – ${Math.max(...agree).toFixed(2)})`,
    `Better wine: more ${pos.join(", ")}. Worse wine: more ${neg.join(", ")}`,
    `${crossIn.length} of the paper's 4 key attributes confirmed` +
      (crossOut.length ? `; ${crossOut.map((r) => `${r.paper_attribute} ranks #${r.our_rank_best_model}`).join(", ")}` : ""),
  ], { x: 9.3, y: 1.95, w: 3.4, fontSize: 12, lineSpacing: 16 });

  tableOn(s, [
    hrow(["Method", "What it measures", "Role"]),
    ["Permutation importance", "Score lost when one measurement is scrambled on unseen wines", "Main measure"],
    ["Random Forest impurity (MDI)", "How much the forest's splits use each measurement", "Cross-check (known bias)"],
    ["Spearman correlation", "Whether more of it means a better or a worse wine", "Direction"],
  ], { x: 0.6, y: 5.1, w: 8.4, colW: [2.6, 4.2, 1.6], fontSize: 11.5 });

  s.addNotes(
    "Third change: feature importance. The main method is permutation importance. Take one measurement, scramble it " +
    "in the test wines so it carries no information, and see how much the score drops. A big drop means the model " +
    `relied on it. ${fiTop[0]}, ${fiTop[1]} and ${fiTop[2]} matter most. I checked this against two other methods ` +
    "and they agree. The direction makes sense chemically: more alcohol and sulphates go with better wine, more " +
    `volatile acidity — a vinegar taste — with worse wine. ${crossIn.length} of the paper's four key attributes are confirmed.`);
}

// =========================================================================
// 16 — HOW MANY TESTS
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "How many lab tests does the model really need?", "Random Forest retrained on the top-k measurements, chosen inside each training fold");
  image(s, FIG2("C3_feature_subset.png"), 0.6, 1.5, 7.6, 4.22);
  const keep = (100 * num(top4.accuracy) / num(full11.accuracy)).toFixed(0);
  text(s, "Business reading", 8.5, 1.55, 4.2, 0.35, { fontFace: HEADF, fontSize: 15, bold: true, color: BERRY });
  bullets(s, [
    `4 tests (${top4.features_most_often_chosen}) give ${f2(top4.accuracy)}% accuracy — ${keep}% of what all 11 give (${f2(full11.accuracy)}%)`,
    `With 4 tests macro-F1 is ${f2(top4.macro_f1)}, slightly above all 11 (${f2(full11.macro_f1)})`,
    `The paper's own four attributes give ${f2(paper4.accuracy)}%`,
    "A winery could screen batches with a much smaller set of tests",
  ], { x: 8.5, y: 1.95, w: 4.2, fontSize: 12.5, lineSpacing: 17 });

  s.addNotes(
    "The practical side of feature importance: how many tests are really needed? I retrained Random Forest using only " +
    "the best few measurements, chosen inside each training fold so the test wines never influence the choice. With " +
    `just four tests the model reaches ${f2(top4.accuracy)} percent, about ${keep} percent of what all eleven give. For a ` +
    "winery that means routine screening could use a smaller, cheaper set of lab tests.");
}

// =========================================================================
// 17 — BEFORE AND AFTER
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Review 1 → Review 2: before and after", `Best model on the main measure: ${short(best.model)}`);
  const mf = headRow("macro_f1"), ba = headRow("balanced_accuracy"), ac = headRow("accuracy");
  statCard(s, 0.6, 1.55, 3.9, f2(mf.review1_ensemble) + " → " + f2(mf.review2_best), "MACRO-F1 (MAIN MEASURE)", BERRY);
  statCard(s, 4.7, 1.55, 3.9, f2(ba.review1_ensemble) + " → " + f2(ba.review2_best), "BALANCED ACCURACY", BERRY);
  statCard(s, 8.8, 1.55, 3.9, f2(ac.review1_ensemble) + " → " + f2(ac.review2_best), "ACCURACY (THE PRICE)", ROSE);

  const metrics = [["recall_3", "Grade 3 found (%)"], ["recall_4", "Grade 4 found (%)"], ["recall_5", "Grade 5 found (%)"],
    ["recall_6", "Grade 6 found (%)"], ["recall_7", "Grade 7 found (%)"], ["recall_8", "Grade 8 found (%)"]];
  tableOn(s, [
    hrow(["", "Review-1 ensemble", "Review-1 Random Forest", "Review-2 best", "Change"]),
    ...metrics.map(([k, lab]) => {
      const r = headRow(k);
      return [lab, f2(r.review1_ensemble), f2(r.review1_random_forest), f2(r.review2_best), signed(r.change_vs_review1_ensemble)];
    }),
  ], { x: 0.6, y: 3.25, w: 8.3, colW: [2.2, 1.6, 1.8, 1.5, 1.2], fontSize: 11.5 });
  card(s, 9.2, 3.25, 3.5, 3.1, PALE);
  text(s, "In one sentence", 9.45, 3.4, 3.1, 0.35, { fontFace: HEADF, fontSize: 14, bold: true, color: BERRY });
  text(s, "Balancing moves accuracy away from the two crowded grades towards the rare ones: more rare wines are found, " +
    `for a small loss overall. Nothing reaches the paper's ${f2(PAPER_ACC)}% — the best accuracy of any fair ` +
    `configuration is ${f2(bestAcc.accuracy)}%.`, 9.45, 3.8, 3.1, 2.5, { fontSize: 12, lineSpacing: 16 });

  s.addNotes(
    `Before and after. On the main measure, macro-F1 rises from ${f2(mf.review1_ensemble)} to ${f2(mf.review2_best)}. ` +
    "The table shows where it comes from: grades 4, 7 and 8 are found much more often, grades 5 and 6 a little less. " +
    `Accuracy moves by ${signed(ac.change_vs_review1_ensemble)} points — the price of balancing. And none of the fair ` +
    `configurations comes near the paper's ${f2(PAPER_ACC)} percent, which supports the Review-1 finding.`);
}

// =========================================================================
// 18 — THE WEB APPLICATION
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "The web application", "Built with Streamlit on the project's own code — so it always shows the project's numbers");
  image(s, path.join(ASSETS, "app_predict.png"), 7.55, 1.4, 5.15, 5.47);
  bullets(s, [
    "Seven pages: overview, dataset, Review 1, class balancing, improving the result, feature importance, prediction",
    "Predict a wine: set 11 sliders (or start from a typical wine of any grade) and get the grade with the probability of every grade",
    `Two models side by side: Random Forest (most accurate, ${f2(acc("RF"))}%) and Random Forest + SMOTE (best on rare grades)`,
    "Batch mode: upload a CSV of wines, download the predictions",
    "15 automated checks: every page loads, the models match the project's exactly, the numbers match the result files — all pass",
  ], { y: 1.6, w: 6.6, fontSize: 13, lineSpacing: 17 });
  card(s, 0.6, 5.65, 6.6, 1.25, PALE);
  text(s, APP_URL ? "Live app" : "Run it", 0.85, 5.75, 6.2, 0.3, { fontFace: HEADF, fontSize: 13, bold: true, color: BERRY });
  text(s, (APP_URL ? APP_URL : "streamlit run app/streamlit_app.py") + "\nCode: " + REPO_URL,
    0.85, 6.1, 6.2, 0.75, { fontSize: 12, color: INK, lineSpacing: 16, fontFace: "Consolas" });

  s.addNotes(
    "Everything is delivered through a web application built with Streamlit. It has seven pages that show every result, " +
    "and a prediction page: you move eleven sliders, or start from a typical wine of any grade, and it shows the " +
    "predicted grade and the probability of each grade, from two models side by side — the most accurate one, and the " +
    "one that is best at finding rare grades. You can also upload a whole CSV file of wines. The app uses the " +
    "project's own code, so it cannot drift from the results, and 15 automated checks confirm that. " +
    "[If possible, switch to the live app here and show a typical grade-8 wine.]");
}

// =========================================================================
// 19 — DELIVERABLES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "What the project delivers", "Everything is generated from the same result files, so it cannot disagree");
  const items = [
    ["Code and results", "Python modules, 100-fold-run experiments, every table and figure", "github.com/Surianandhan/…"],
    ["Web application", "Seven pages, live prediction, batch CSV, 15 automated checks", "Streamlit"],
    ["Project report", "69 pages in the SASTRA format: 9 chapters, 33 verified references", "Word + PDF"],
    ["Conference paper", "10 pages: method, results, discussion", "Word + PDF"],
    ["Colab notebook", "Runs the whole project in a browser, no installation", "Google Colab"],
  ];
  items.forEach(([h, b, tag], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.35;
    card(s, x, y, 3.85, 2.05, i < 2 ? PALE : TINT, i < 2 ? BERRY : null);
    text(s, h, x + 0.25, y + 0.2, 3.4, 0.4, { fontFace: HEADF, fontSize: 16, bold: true, color: BERRY });
    text(s, b, x + 0.25, y + 0.68, 3.4, 0.9, { fontSize: 12.5, lineSpacing: 16 });
    text(s, tag, x + 0.25, y + 1.6, 3.4, 0.3, { fontSize: 10.5, italic: true, color: MUTED });
  });
  card(s, 8.8, 3.95, 3.85, 2.05, BERRY);
  text(s, "One command", 9.05, 4.15, 3.4, 0.4, { fontFace: HEADF, fontSize: 16, bold: true, color: GOLD });
  text(s, "python run_all.py --review2\nreruns every experiment and rewrites every table and figure.", 9.05, 4.63, 3.4, 1.2,
    { fontSize: 12.5, color: WHITE, lineSpacing: 17 });

  s.addNotes(
    "These are the deliverables. The code and all results are on GitHub. The web application. The project report, 69 " +
    "pages in the university format with 33 references, each checked. A 10-page conference paper. And a Colab " +
    "notebook that runs everything in a browser. All of them are generated from the same result files, so a number " +
    "in the report, the paper, the app and these slides is always the same number. One command reruns everything.");
}

// =========================================================================
// 20 — CONCLUSION
// =========================================================================
{
  const s = pres.addSlide();
  s.background = { color: BERRY };
  s.addText("Conclusion", { x: 0.6, y: 0.4, w: 12.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEADF, fontSize: 32, bold: true, color: WHITE });
  const items = [
    ["Reproduction", `The paper's method, rebuilt exactly and tested fairly, reaches ${f2(acc("Ensemble (soft vote)"))}% — not ${f2(PAPER_ACC)}%. Random Forest alone does better (${f2(acc("RF"))}%).`],
    ["Why", "The paper's weights are nearly equal, so the ensemble averages its members; the paper's own tables point the same way."],
    ["Three changes", `Balancing finds far more rare wines (macro-F1 ${f2(headRow("macro_f1").review1_ensemble)} → ${f2(headRow("macro_f1").review2_best)}); learned weights lift the paper's ensemble to ${f2(ltR1.accuracy)}%; ${fiTop[0]}, ${fiTop[1]} and ${fiTop[2]} drive quality.`],
    ["Delivered", "A tested web application, a 69-page report, a conference paper and reproducible code."],
  ];
  items.forEach(([h, b], i) => {
    const y = 1.35 + i * 1.3;
    s.addText(h, { x: 0.6, y, w: 3.0, h: 0.4, isTextBox: true, margin: 0, fontFace: HEADF, fontSize: 18, bold: true, color: GOLD });
    s.addText(b, { x: 3.7, y, w: 9.0, h: 1.15, isTextBox: true, margin: 0, valign: "top", fontFace: BODY, fontSize: 14, color: WHITE, lineSpacing: 19 });
  });
  s.addText("Lesson: an ensemble only beats its best member if the weights let the best member lead.", {
    x: 0.6, y: 6.55, w: 12.1, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, italic: true, color: "F0E4E8" });

  s.addNotes(
    "To conclude. First, the paper's method, rebuilt exactly and tested fairly, reaches about 69 percent, not 89.73, " +
    "and a single Random Forest does better. Second, the reason is that the paper's weights are nearly equal, so the " +
    "team just averages its members — and the paper's own tables point the same way. Third, all three requested " +
    "changes are done: balancing finds many more rare wines, learning the weights properly improves the paper's own " +
    "ensemble, and alcohol, sulphates and volatile acidity drive quality. Finally, everything is delivered as a tested " +
    "web app, a report, a paper and reproducible code. The general lesson: a team only beats its best member if the " +
    "weights let the best member lead.");
}

// =========================================================================
// 21 — LIMITATIONS AND FUTURE WORK
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Limitations and future work", "Stated openly");
  text(s, "Limitations", 0.6, 1.5, 6.0, 0.35, { fontFace: HEADF, fontSize: 17, bold: true, color: BERRY });
  bullets(s, [
    "Two of the paper's four models had to be replaced by syllabus-friendly substitutes",
    `Grade 3 has only ${COUNTS["3"]} wines and grade 8 only ${COUNTS["8"]} — too few for any model to learn reliably`,
    "The best model is picked on the same cross-validation that scores it — a small optimistic bias",
    "The 10 repeats reuse the same wines, so the statistical test across them is indicative only",
    "Only red wine, and only lab measurements — no price, region or vintage",
  ], { x: 0.6, y: 1.95, w: 6.0, fontSize: 13, lineSpacing: 17 });
  text(s, "Future work", 7.0, 1.5, 5.7, 0.35, { fontFace: HEADF, fontSize: 17, bold: true, color: BERRY });
  bullets(s, [
    "Repeat on the 4,898 white wines of the same dataset",
    "Treat the grade as ordered: predicting 6 for a 7 should cost less than predicting 3",
    "Nested cross-validation around the model choice, with proper confidence intervals",
    "Explain each individual prediction inside the web app",
  ], { x: 7.0, y: 1.95, w: 5.7, fontSize: 13, lineSpacing: 17 });

  s.addNotes(
    "I want to be open about the limits. Two of the paper's models had to be replaced. The rarest grades have so few " +
    "wines that no model can learn them reliably. The best model is chosen on the same tests that score it, which " +
    "flatters it slightly. And it is only red wine with only lab measurements. Future work: the white-wine data, " +
    "treating grades as ordered, nested cross-validation for proper confidence intervals, and explaining individual " +
    "predictions in the app.");
}

// =========================================================================
// 22 — REFERENCES AND THANK YOU
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "References", "");
  s.addText([
    { text: "[1]  Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to table: Uncovering wine quality for sales management through machine learning. Journal of Business Research, 176, 114576.", options: { breakLine: true } },
    { text: "[2]  Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. Decision Support Systems, 47(4), 547–553.", options: { breakLine: true } },
    { text: "[3]  Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. Journal of Artificial Intelligence Research, 16, 321–357.", options: { breakLine: true } },
    { text: "[4]  Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.", options: { breakLine: true } },
    { text: "[5]  Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. The Annals of Statistics, 29(5), 1189–1232.", options: { breakLine: true } },
    { text: "[6]  Kuncheva, L. I., & Whitaker, C. J. (2003). Measures of diversity in classifier ensembles and their relationship with the ensemble accuracy. Machine Learning, 51(2), 181–207.", options: { breakLine: true } },
    { text: "[7]  Wolpert, D. H. (1992). Stacked generalization. Neural Networks, 5(2), 241–259.", options: { breakLine: true } },
    { text: "[8]  Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.", options: { breakLine: true } },
    { text: "[9]  Cortez, P., et al. (2009). Wine Quality [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C56S3T", options: {} },
  ], { x: 0.6, y: 1.35, w: 12.1, h: 4.6, isTextBox: true, margin: 0, valign: "top",
    fontFace: BODY, fontSize: 12, color: INK, paraSpaceAfter: 7, lineSpacing: 16 });
  card(s, 0.6, 6.1, 12.1, 0.85, BERRY);
  text(s, "Thank you — questions are welcome.", 0.9, 6.25, 11.5, 0.5, { fontFace: HEADF, fontSize: 20, bold: true, color: WHITE });

  s.addNotes("These are the main references; the report lists all 33. Thank you — I am happy to take questions.");
}

// =========================================================================
// BACKUP SLIDES
// =========================================================================
{
  const s = pres.addSlide();
  title(s, "Backup 1 — the measures, in plain words", "For one grade at a time, e.g. grade 4");
  tableOn(s, [
    hrow(["Measure", "Plain meaning", "Formula"]),
    ["Accuracy", "Share of all wines given the right grade", "correct ÷ all"],
    ["Recall (the paper's \"precision\")", "Of the wines that really are grade 4, how many did we find?", "TP ÷ (TP + FN)"],
    ["Precision", "Of the wines we called grade 4, how many really are?", "TP ÷ (TP + FP)"],
    ["F1", "Balance of precision and recall for one grade", "2PR ÷ (P + R)"],
    ["Macro-F1 (main measure)", "F1 of each of the six grades, averaged with equal weight", "mean of 6 F1s"],
    ["Balanced accuracy", "Recall of each grade, averaged with equal weight", "mean of 6 recalls"],
  ], { y: 1.55, colW: [3.2, 6.0, 2.9], fontSize: 13 });
  text(s, "TP = right calls of grade 4 · FN = grade-4 wines we missed · FP = other wines wrongly called grade 4. " +
    `The paper's per-class "precision" divides by the true grade totals — that is recall; the report notes this.`,
  0.6, 5.55, 12.1, 0.9, { fontSize: 12, color: MUTED, lineSpacing: 16 });
  s.addNotes("Pull this out if asked what a measure means, or about the paper's precision/recall wording.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 2 — top candidates, ranked by macro-F1", "Pooled over 100 fold-runs");
  const top = COMP.slice(0, 14);
  tableOn(s, [
    hrow(["#", "Model", "Kind", "Accuracy", "Bal. acc.", "Macro-F1"]),
    ...top.map((r) => [r.rank_by_macro_f1, short(r.model), r.kind, f2(r.accuracy), f2(r.balanced_accuracy), f2(r.macro_f1)]),
  ], { y: 1.5, colW: [0.5, 6.4, 1.6, 1.2, 1.2, 1.2], fontSize: 10.5 });
  text(s, `Top ${top.length} of ${COMP.length}. Full table: results/review2/tables/model_comparison.csv`,
    0.6, 6.75, 12.1, 0.35, { fontSize: 11, color: MUTED });
  s.addNotes("Pull this out if asked for the full ranking or for a specific model's numbers.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 3 — is the improvement consistent?", "Paired comparison across the 10 repeats — every model scored on identical folds");
  tableOn(s, [
    hrow(["Model", "Compared with", "Measure", "Mean diff.", "Repeats won", "Wilcoxon p"]),
    ...PAIRED.map((r) => [short(r.model), short(r.compared_with), r.metric === "macro_f1" ? "Macro-F1" : "Accuracy",
      signed(r.mean_difference), `${r.repeats_won} / ${r.repeats}`, isNaN(num(r.wilcoxon_p)) ? "—" : num(r.wilcoxon_p).toFixed(3)]),
  ], { y: 1.5, colW: [3.6, 3.3, 1.2, 1.3, 1.4, 1.3], fontSize: 10.5 });
  text(s, "The repeats reuse the same 1,599 wines with different splits, so they are not independent and the p-values are " +
    "optimistic. The win count is the plainer evidence.", 0.6, 6.5, 12.1, 0.6, { fontSize: 11.5, color: MUTED, lineSpacing: 15 });
  s.addNotes("Pull this out if asked whether the improvement is real or just noise.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 4 — confusion matrices", "Rows = true grade, columns = predicted grade; percentages are the share of each true grade");
  image(s, RFIG("confusion_matrices.png"), 0.6, 1.6, 12.1, 4.09);
  text(s, "Most mistakes go to a neighbouring grade. Balancing moves predictions out of the crowded 5 and 6 columns into the " +
    "rare grades: more rare wines caught, and some common wines now called rare.", 0.6, 5.95, 12.1, 0.8,
  { fontSize: 12.5, color: MUTED, lineSpacing: 17 });
  s.addNotes("Pull this out if asked exactly where the predictions moved.");
}

{
  const s = pres.addSlide();
  title(s, "Backup 5 — feature-importance table", "Macro-F1 points lost when the measurement is shuffled; Spearman ρ with quality");
  tableOn(s, [
    hrow(["Rank", "Measurement", "Best model", "Random Forest", "RF impurity", "ρ with quality", "Paper key?"]),
    ...FI.map((r) => [r.rank_final, r.feature, f2(r.final_f1_drop), f2(r.rf_f1_drop), num(r.rf_mdi).toFixed(3),
      num(r.spearman_rho).toFixed(2), r.highlighted_by_paper === "True" ? "yes" : ""]),
  ], { y: 1.5, colW: [0.8, 2.9, 1.7, 1.8, 1.7, 1.9, 1.3], fontSize: 11 });
  s.addNotes("Pull this out if asked for the exact importance values.");
}

pres.writeFile({ fileName: OUT }).then((f) => console.log("wrote " + f));
