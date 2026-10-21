"""
evaluate.py

Confusion matrices and per-class metrics for each base learner and the final
ensemble, plus a benchmark comparison against the published numbers from
Cortez et al. (2009) and Ma et al. (2024).

A note on "precision" terminology
----------------------------------
Ma et al. (2024) label their per-class metric "precision," but their own
worked example (Eq. 14 in the paper: 137 / (137+1+2+58+6) = 67.16% for class
5) divides the diagonal count by the *total number of samples actually
belonging to that class* -- i.e. TP / (TP + FN). That is the standard
definition of recall / sensitivity, not precision (TP / (TP + FP)). To keep
our benchmark comparison numerically comparable to the numbers Ma et al. and
Cortez et al. published, we reproduce their metric under their definition,
but we label it explicitly as "precision (paper definition = recall)" and
also report conventional precision/recall/specificity separately so the two
are never conflated.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score

from config import (
    BENCHMARK_CLASSES,
    CORTEZ_2009_PER_CLASS_PRECISION,
    FIGURES_DIR,
    LITERATURE_ACCURACY_RANGE_PCT,
    MA_2024_BASE_LEARNER_ACCURACY,
    MA_2024_OVERALL_ACCURACY,
    MA_2024_PER_CLASS_PRECISION,
    MA_2024_TABLE8_WEIGHT_SUM,
    MA_2024_TABLE9_CONFUSION,
    TABLES_DIR,
)


def specificity_per_class(cm):
    """One-vs-rest specificity = TN / (TN + FP) for each class, from a
    standard sklearn confusion matrix (rows=true, columns=predicted)."""
    n = cm.shape[0]
    total = cm.sum()
    spec = np.zeros(n)
    for i in range(n):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = total - tp - fp - fn
        spec[i] = tn / (tn + fp) if (tn + fp) > 0 else np.nan
    return spec


def per_class_metrics(y_true, y_pred, classes):
    """Per-class precision, recall/sensitivity, specificity, and the paper's
    "precision" (numerically identical to recall -- see module docstring)."""
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    precision = precision_score(y_true, y_pred, labels=classes, average=None, zero_division=0)
    recall = recall_score(y_true, y_pred, labels=classes, average=None, zero_division=0)
    specificity = specificity_per_class(cm)

    return pd.DataFrame(
        {
            "class": classes,
            "n_actual": cm.sum(axis=1),
            "precision": precision * 100,
            "sensitivity_recall": recall * 100,
            "specificity": specificity * 100,
            "precision_paper_definition_pct": recall * 100,  # see module docstring
        }
    )


def overall_accuracy(y_true, y_pred):
    return float((np.asarray(y_true) == np.asarray(y_pred)).mean()) * 100


def confusion_matrix_df(y_true, y_pred, classes):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    return pd.DataFrame(cm, index=[f"true_{c}" for c in classes], columns=[f"pred_{c}" for c in classes])


def save_model_evaluation(name, y_true, y_pred, classes, tables_dir=TABLES_DIR):
    tables_dir.mkdir(parents=True, exist_ok=True)
    cm_df = confusion_matrix_df(y_true, y_pred, classes)
    cm_df.to_csv(tables_dir / f"confusion_matrix_{name}.csv")

    metrics_df = per_class_metrics(y_true, y_pred, classes)
    metrics_df.attrs["overall_accuracy_pct"] = overall_accuracy(y_true, y_pred)
    metrics_df.to_csv(tables_dir / f"metrics_{name}.csv", index=False)

    return cm_df, metrics_df


def build_benchmark_comparison(our_metrics_df, our_overall_accuracy, tables_dir=TABLES_DIR):
    """Build the reproduction-vs-published comparison table (per class +
    overall), matching the classes/order Ma et al. (2024) report in Table 9."""
    our_by_class = our_metrics_df.set_index("class")["precision_paper_definition_pct"]
    our_values = [our_by_class.get(c, np.nan) for c in BENCHMARK_CLASSES]

    comparison = pd.DataFrame(
        {
            "class": BENCHMARK_CLASSES + ["overall"],
            "cortez_2009_pct": CORTEZ_2009_PER_CLASS_PRECISION + [np.nan],
            "ma_2024_pct": MA_2024_PER_CLASS_PRECISION + [MA_2024_OVERALL_ACCURACY],
            "our_reproduction_pct": list(our_values) + [our_overall_accuracy],
        }
    )
    tables_dir.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(tables_dir / "benchmark_comparison.csv", index=False)
    return comparison


def plot_benchmark_comparison(comparison_df, figures_dir=FIGURES_DIR, filename="accuracy_comparison.png"):
    """Grouped bar chart: our reproduction vs. Ma et al. (2024) vs. Cortez et
    al. (2009), per class and overall."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    labels = [str(c) for c in comparison_df["class"]]
    x = np.arange(len(labels))
    width = 0.26

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width, comparison_df["cortez_2009_pct"], width, label="Cortez et al. (2009)")
    ax.bar(x, comparison_df["ma_2024_pct"], width, label="Ma et al. (2024) ensemble")
    ax.bar(x + width, comparison_df["our_reproduction_pct"], width, label="Our reproduction")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Quality class (last bar group = overall accuracy)")
    ax.set_ylabel("Precision / accuracy (%)  [paper's precision = per-class recall]")
    ax.set_title("Reproduction vs. published benchmarks")
    ax.legend()
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(figures_dir / filename, dpi=150)
    plt.close(fig)


def paper_table9_reconciliation(tables_dir=TABLES_DIR):
    """Check Ma et al. (2024)'s reported headline figures against their own Table 9.

    The paper states 89.73% overall accuracy from "10 runs of 10-fold
    cross-validation" (100 experiments over all 1599 samples). We recompute
    directly from the confusion matrix they print, to understand the gap
    between their result and ours.

    IMPORTANT CAVEAT: the matrix in config.MA_2024_TABLE9_CONFUSION was
    transcribed by eye from the printed PDF table and may contain reading
    errors. Everything below is therefore reported as "we could not reconcile",
    not as a claim that the paper is wrong.
    """
    cm = np.array(MA_2024_TABLE9_CONFUSION, dtype=int)
    total_n = int(cm.sum())
    diagonal = int(np.trace(cm))
    implied_accuracy = 100.0 * diagonal / total_n

    # Their per-class percentages: does TP/column-total or TP/row-total reproduce them?
    col_totals = cm.sum(axis=0)
    row_totals = cm.sum(axis=1)
    tp = np.diag(cm)
    col_wise = np.where(col_totals > 0, 100.0 * tp / np.maximum(col_totals, 1), np.nan)
    row_wise = np.where(row_totals > 0, 100.0 * tp / np.maximum(row_totals, 1), np.nan)

    per_class = pd.DataFrame(
        {
            "class": BENCHMARK_CLASSES,
            "paper_reported_pct": MA_2024_PER_CLASS_PRECISION,
            "recomputed_column_wise_pct": np.round(col_wise, 2),
            "recomputed_row_wise_pct": np.round(row_wise, 2),
        }
    )
    per_class["column_wise_matches"] = np.isclose(
        per_class["paper_reported_pct"], per_class["recomputed_column_wise_pct"], atol=0.6
    )

    lo, hi = LITERATURE_ACCURACY_RANGE_PCT
    summary = pd.DataFrame(
        [
            ("implied_test_set_size", total_n),
            ("full_dataset_size", 1599),
            ("implied_fraction_of_dataset_pct", round(100.0 * total_n / 1599, 2)),
            ("correct_predictions_on_diagonal", diagonal),
            ("implied_overall_accuracy_pct", round(implied_accuracy, 2)),
            ("paper_reported_overall_accuracy_pct", MA_2024_OVERALL_ACCURACY),
            ("discrepancy_pct_points", round(MA_2024_OVERALL_ACCURACY - implied_accuracy, 2)),
            ("n_per_class_matching_column_wise", int(per_class["column_wise_matches"].sum())),
            ("literature_accuracy_range_pct", f"{lo}-{hi}"),
        ],
        columns=["quantity", "value"],
    )

    tables_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(tables_dir / "paper_table9_reconciliation.csv", index=False)
    per_class.to_csv(tables_dir / "paper_table9_per_class_check.csv", index=False)
    return summary, per_class


def paper_internal_consistency_check(our_ensemble_accuracy=None, tables_dir=TABLES_DIR):
    """Check the paper's ensemble result against its own base-learner numbers.

    Ma et al. report, in their own tables: base-learner accuracies of 67.30
    (SVM), 61.43 (RNN), 55.77 (ELM), 80.71 (RF) in Tables 4-7; near-uniform
    final weights of 0.2516 / 0.2286 / 0.2168 / 0.3030 in Table 8; and an
    ensemble accuracy of 89.73%.

    Applying their Table 8 weights to their Table 4-7 accuracies gives a
    weighted-average accuracy in the high 60s. A voting ensemble is not simply
    the weighted average of its members' accuracies -- decorrelated errors let
    a good ensemble exceed that baseline -- so this is an indicative reference
    point, not a proof. But exceeding it by ~22 percentage points, while using
    weights that are within 0.05 of uniform, is a large gap to explain.

    We report the number and let the reader judge. Our own ensemble result
    lands close to this weighted-average baseline, which is what one would
    expect from near-uniform weights.
    """
    weights = MA_2024_TABLE8_WEIGHT_SUM
    accuracies = MA_2024_BASE_LEARNER_ACCURACY
    weighted_avg = sum(weights[k] * accuracies[k] for k in weights)
    best_base = max(accuracies.values())
    uniform = 1.0 / len(weights)
    max_dev = max(abs(w - uniform) for w in weights.values())

    rows = [
        ("weight_sum_total", round(sum(weights.values()), 4)),
        ("max_abs_deviation_from_uniform_weight", round(max_dev, 4)),
        ("best_single_base_learner_pct", best_base),
        ("weighted_average_of_base_accuracies_pct", round(weighted_avg, 2)),
        ("paper_reported_ensemble_pct", MA_2024_OVERALL_ACCURACY),
        ("gap_vs_weighted_average_pct_points", round(MA_2024_OVERALL_ACCURACY - weighted_avg, 2)),
        ("gap_vs_best_base_learner_pct_points", round(MA_2024_OVERALL_ACCURACY - best_base, 2)),
    ]
    if our_ensemble_accuracy is not None:
        rows.append(("our_ensemble_pct", round(our_ensemble_accuracy, 2)))
        rows.append(
            ("our_gap_vs_their_weighted_average_pct_points", round(our_ensemble_accuracy - weighted_avg, 2))
        )

    check = pd.DataFrame(rows, columns=["quantity", "value"])
    tables_dir.mkdir(parents=True, exist_ok=True)
    check.to_csv(tables_dir / "paper_internal_consistency_check.csv", index=False)
    return check


def build_accuracy_summary(pooled_true, pooled_preds, pooled_ensemble, pooled_ensemble_hard=None,
                           tables_dir=TABLES_DIR):
    """One row per model, sorted best-first, so the ensemble-vs-base-learner
    comparison (the paper's central claim) can be checked at a glance."""
    rows = [
        {"model": name, "overall_accuracy_pct": overall_accuracy(pooled_true, preds)}
        for name, preds in pooled_preds.items()
    ]
    rows.append(
        {"model": "Ensemble (soft vote)", "overall_accuracy_pct": overall_accuracy(pooled_true, pooled_ensemble)}
    )
    if pooled_ensemble_hard is not None:
        rows.append(
            {
                "model": "Ensemble (hard vote)",
                "overall_accuracy_pct": overall_accuracy(pooled_true, pooled_ensemble_hard),
            }
        )

    summary = pd.DataFrame(rows).sort_values("overall_accuracy_pct", ascending=False).reset_index(drop=True)
    summary["rank"] = summary.index + 1
    tables_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(tables_dir / "model_accuracy_summary.csv", index=False)
    return summary


def evaluate_all(pooled_true, pooled_preds, pooled_ensemble, classes, pooled_ensemble_hard=None,
                 tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    """Run save_model_evaluation for every base learner plus the ensemble,
    then build and plot the benchmark comparison. Returns dict[name] -> (cm_df, metrics_df).

    `tables_dir` / `figures_dir` default to the project's results/ folders. Pass a
    scratch directory when running an exploratory experiment (e.g. the walkthrough
    notebook, which uses fewer CV repeats) so that partial results cannot silently
    overwrite the canonical outputs quoted in README.md and report/methodology.md.
    """
    all_results = {}
    for name, preds in pooled_preds.items():
        all_results[name] = save_model_evaluation(name, pooled_true, preds, classes, tables_dir=tables_dir)

    ensemble_cm, ensemble_metrics = save_model_evaluation(
        "Ensemble", pooled_true, pooled_ensemble, classes, tables_dir=tables_dir
    )
    all_results["Ensemble"] = (ensemble_cm, ensemble_metrics)

    if pooled_ensemble_hard is not None:
        all_results["Ensemble_hard_vote"] = save_model_evaluation(
            "Ensemble_hard_vote", pooled_true, pooled_ensemble_hard, classes, tables_dir=tables_dir
        )

    ensemble_overall_acc = overall_accuracy(pooled_true, pooled_ensemble)
    comparison = build_benchmark_comparison(ensemble_metrics, ensemble_overall_acc, tables_dir=tables_dir)
    plot_benchmark_comparison(comparison, figures_dir=figures_dir)
    build_accuracy_summary(
        pooled_true, pooled_preds, pooled_ensemble, pooled_ensemble_hard, tables_dir=tables_dir
    )
    paper_table9_reconciliation(tables_dir=tables_dir)
    paper_internal_consistency_check(our_ensemble_accuracy=ensemble_overall_acc, tables_dir=tables_dir)

    return all_results, comparison


if __name__ == "__main__":
    from ensemble import run_repeated_cv
    from preprocessing import load_red_wine_xy

    X, y, feature_columns, _ = load_red_wine_xy()
    results = run_repeated_cv(X, y, n_repeats=2)
    _, comparison = evaluate_all(
        results["pooled_true"],
        results["pooled_preds"],
        results["pooled_ensemble"],
        results["classes"],
        pooled_ensemble_hard=results["pooled_ensemble_hard"],
    )
    print(comparison)
    print()
    summary, per_class = paper_table9_reconciliation()
    print(summary.to_string(index=False))
