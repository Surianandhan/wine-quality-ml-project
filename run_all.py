"""
run_all.py

Single entry point for the reproduction of Ma et al. (2024).

Usage:
    python run_all.py                    # full protocol: 10-fold CV x 10 repeats
    python run_all.py --quick            # fast sanity pass: 10-fold CV x 2 repeats
    python run_all.py --review2          # + Review 2: class balancing, improvements,
                                         #   feature importance (about 45-60 min)
    python run_all.py --quick --review2  # the same at 2 repeats, to a scratch folder
    python run_all.py --with-novelty     # also run the optional Step 4 extension

By default this runs the base-paper reproduction only. The clustering /
outlier-detection / association-rule extension is optional coursework and is
kept out of the default path -- pass --with-novelty to include it.

All tables are written to results/tables/, all figures to results/figures/.
Review 2 writes to results/review2/{tables,figures}/ so the Review-1 numbers
are never overwritten.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from config import (  # noqa: E402
    FIGURES_DIR,
    N_REPEATS,
    QUICK_N_REPEATS,
    QUICK_OUTPUT_DIR,
    QUICK_REVIEW2_DIR,
    REVIEW2_FIGURES_DIR,
    REVIEW2_TABLES_DIR,
    TABLES_DIR,
)
from ensemble import run_repeated_cv, weight_concentration  # noqa: E402
from evaluate import (  # noqa: E402
    evaluate_all,
    paper_internal_consistency_check,
    paper_table9_reconciliation,
    per_class_metrics,
)
from preprocessing import load_red_wine_xy  # noqa: E402


def step3_reproduction(X, y, n_repeats, tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    print("=" * 72)
    print("STEP 3: Base paper reproduction (classical-ML substitutions)")
    print("=" * 72)

    results = run_repeated_cv(X, y, n_repeats=n_repeats)
    all_results, comparison = evaluate_all(
        results["pooled_true"],
        results["pooled_preds"],
        results["pooled_ensemble"],
        results["classes"],
        pooled_ensemble_hard=results["pooled_ensemble_hard"],
        tables_dir=tables_dir,
        figures_dir=figures_dir,
    )

    print("\n-- Model ranking (pooled over all repeats) --")
    summary = pd.read_csv(tables_dir / "model_accuracy_summary.csv")
    print(summary.to_string(index=False))

    print("\n-- Per-class comparison vs. published benchmarks --")
    print(comparison.to_string(index=False))

    print("\n-- Ensemble weights, and why they matter --")
    conc = weight_concentration(results["per_repeat"][0]["weights"])
    for key, value in conc.items():
        print(f"  {key}: {value}")
    print(
        "  (Weights close to uniform => the ensemble approximates a plain average\n"
        "   of its members, which lands between the strongest and weakest learner.)"
    )

    print("\n-- Reconciling the paper's reported 89.73% against its own Table 9 --")
    recon, per_class_check = paper_table9_reconciliation()
    print(recon.to_string(index=False))
    print("\n  Per-class check (does their 'precision' reproduce column-wise?):")
    print(per_class_check.to_string(index=False))
    print(
        "\n  CAVEAT: Table 9 was transcribed by eye from the printed PDF and may\n"
        "  contain reading errors. Reported as 'could not reconcile', not as a\n"
        "  claim that the paper is incorrect."
    )

    print("\n-- Paper internal consistency: Table 8 weights x Tables 4-7 accuracies --")
    ens_acc = 100.0 * (results["pooled_ensemble"] == results["pooled_true"]).mean()
    print(paper_internal_consistency_check(our_ensemble_accuracy=ens_acc).to_string(index=False))

    return results, all_results, comparison


def step4_novelty(X, y, df, baseline_all_results, n_repeats):
    """Optional extension -- only runs with --with-novelty."""
    from config import FEATURE_COLUMNS
    from novelty_cluster_mine_feedback import (
        augment_with_cluster_feature,
        compare_cluster_feedback,
        crosscheck_with_paper_figures,
        run_clustering,
        run_frequent_pattern_mining,
        run_outlier_detection,
        save_cluster_feedback_outputs,
        save_clustering_outputs,
        save_mining_outputs,
        save_outlier_outputs,
    )
    from preprocessing import minmax_normalize

    print("\n" + "=" * 72)
    print("STEP 4 (optional): Clustering, outliers, cluster feedback, rule mining")
    print("=" * 72)

    # The unsupervised analyses fit on all rows at once (no train/test split),
    # so scaling the whole matrix here introduces no leakage.
    X_norm, _ = minmax_normalize(X)

    print("\n-- 4a. Clustering --")
    clustering_result = run_clustering(X_norm)
    crosstab = save_clustering_outputs(clustering_result, y)
    print(f"Best clustering: {clustering_result['best_method']} (k={clustering_result['best_k']})")
    print(crosstab)

    print("\n-- 4b. Outlier detection --")
    _, rate_by_class = run_outlier_detection(X_norm, y)
    save_outlier_outputs(rate_by_class)
    print(rate_by_class)

    print("\n-- 4c. Cluster-ID feedback feature --")
    X_aug = augment_with_cluster_feature(X, clustering_result["best_labels"], clustering_result["best_k"])
    aug_results = run_repeated_cv(X_aug, y, n_repeats=n_repeats)
    aug_metrics = per_class_metrics(
        aug_results["pooled_true"], aug_results["pooled_ensemble"], aug_results["classes"]
    )
    feedback_comparison = compare_cluster_feedback(baseline_all_results["Ensemble"][1], aug_metrics)
    save_cluster_feedback_outputs(feedback_comparison)
    print(feedback_comparison.to_string(index=False))

    print("\n-- 4d. Frequent pattern mining --")
    top10, per_cluster = run_frequent_pattern_mining(df, FEATURE_COLUMNS, y, clustering_result["best_labels"])
    crosscheck = crosscheck_with_paper_figures(top10)
    save_mining_outputs(top10, per_cluster, crosscheck)
    print("\nCross-check vs. Ma et al. (2024) Figs. 4-5 key attributes:")
    for key, value in crosscheck.items():
        print(f"  {key}: {sorted(value)}")


def step5_review2(X, y, feature_columns, n_repeats, tables_dir, figures_dir):
    """Review 2: (A) class balancing, (B) improving the result, (C) feature
    importance. Writes to results/review2/ only -- see src/review2.py."""
    import numpy as np

    from config import BENCHMARK_CLASSES, N_REPEATS, REVIEW2_PRIMARY_METRIC
    from feature_importance import run_feature_importance
    from review2 import (
        BALANCING_LABELS,
        PAPER_ENSEMBLE,
        build_model_comparison,
        experiment_a_class_balancing,
        experiment_b1_temperature,
        experiment_b2_b3_improvements,
        headline_table,
        plot_headline,
        paired_comparison,
        per_repeat_scores,
        plot_tradeoff,
        save_confusion,
    )

    print("\n" + "=" * 72)
    print("REVIEW 2: class balancing, improving the result, feature importance")
    print(f"Primary metric, fixed before any Review-2 run: {REVIEW2_PRIMARY_METRIC}")
    print("=" * 72)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    classes = sorted(np.unique(y).tolist())
    y_pooled = np.concatenate([y] * n_repeats)
    show = ["accuracy", "balanced_accuracy", "macro_f1"] + [f"recall_{c}" for c in BENCHMARK_CLASSES]

    print("\n-- A. Class balancing (same four learners, paper's weighted soft vote) --")
    a_df, cache, a_preds = experiment_a_class_balancing(X, y, classes, n_repeats, tables_dir, figures_dir)
    ens = a_df[a_df["model"] == PAPER_ENSEMBLE]
    print(ens[["balancing_label"] + show].round(2).to_string(index=False))

    # The "partial" scheme IS the Review-1 configuration, so on the full
    # protocol it must reproduce the Review-1 ensemble to the last digit.
    if n_repeats == N_REPEATS:
        canon = pd.read_csv(TABLES_DIR / "model_accuracy_summary.csv")
        expected = canon.loc[canon["model"] == "Ensemble (soft vote)", "overall_accuracy_pct"].iloc[0]
        got = ens.loc[ens["balancing"] == "partial", "accuracy"].iloc[0]
        status = "MATCH" if abs(got - expected) < 1e-9 else "MISMATCH -- investigate before trusting Review 2"
        print(f"\n  Regression check vs Review 1: {got:.10f} vs {expected:.10f} -> {status}")

    best_balancing = ens.sort_values(REVIEW2_PRIMARY_METRIC, ascending=False)["balancing"].iloc[0]
    print(f"\n  Best balancing scheme on {REVIEW2_PRIMARY_METRIC}: {BALANCING_LABELS[best_balancing]}")

    print("\n-- B1. Weight sharpening (diagnostic test of the Review-1 explanation) --")
    configs = ["partial"] + ([best_balancing] if best_balancing != "partial" else [])
    b1 = experiment_b1_temperature(cache, y, classes, configs, tables_dir, figures_dir)
    print(b1[["balancing", "sharpen", "temperature", "accuracy", "macro_f1", "rf_accuracy",
              "largest_weight_learner", "largest_weight"]].round(3).to_string(index=False))

    print("\n-- B2/B3. Stacking and stronger learners --")
    b_df, b_preds = experiment_b2_b3_improvements(X, y, classes, n_repeats, cache, tables_dir)
    print(b_df[["model"] + show].round(2).to_string(index=False))

    comp = build_model_comparison(a_df, b_df, tables_dir)
    head, best_name = headline_table(a_df, comp, tables_dir)
    plot_headline(comp, figures_dir)
    plot_tradeoff(comp, figures_dir)
    all_preds = {**a_preds, **b_preds}
    save_confusion(y_pooled, all_preds[best_name], classes, "review2_best", tables_dir)
    save_confusion(y_pooled, a_preds[f"{PAPER_ENSEMBLE} | {BALANCING_LABELS['partial']}"], classes,
                   "review1_ensemble", tables_dir)

    # Keep every candidate's pooled predictions, so any later question can be
    # answered without re-running the whole experiment.
    np.savez_compressed(tables_dir / "pooled_predictions.npz", y_pooled=y_pooled,
                        names=np.array(list(all_preds)), preds=np.array(list(all_preds.values())))

    # Is the improvement consistent across the 10 repeats, or noise?
    r1_ens = f"{PAPER_ENSEMBLE} | {BALANCING_LABELS['partial']}"
    r1_rf = f"RF | {BALANCING_LABELS['partial']}"
    lt_r1 = f"Learned-temperature ensemble | {BALANCING_LABELS['partial']}"
    best_acc_name = comp.sort_values("accuracy", ascending=False)["model"].iloc[0]
    per_rep = per_repeat_scores(all_preds, y, classes, n_repeats)
    per_rep.round(4).to_csv(tables_dir / "per_repeat_scores.csv", index=False)
    runner_up = comp["model"].iloc[1]
    paired = paired_comparison(per_rep, [(best_name, r1_ens), (best_name, r1_rf), (best_name, runner_up),
                                         (lt_r1, r1_ens), (lt_r1, r1_rf), (best_acc_name, r1_ens)], tables_dir)
    print("\n-- Paired comparison across the repeats (wins / Wilcoxon p; p is optimistic, see code) --")
    print(paired.round(4).to_string(index=False))

    print(f"\n-- Every candidate, ranked by {REVIEW2_PRIMARY_METRIC} (top 10) --")
    print(comp[["model", "accuracy", "balanced_accuracy", "macro_f1"]].head(10).round(2).to_string(index=False))
    best_acc = comp.sort_values("accuracy", ascending=False).iloc[0]
    print(f"\n  Best on {REVIEW2_PRIMARY_METRIC}: {best_name}")
    print(f"  Best on accuracy:  {best_acc['model']} ({best_acc['accuracy']:.2f}%)")
    print("\n-- Review 1 vs Review 2 --")
    print(head.round(2).to_string(index=False))

    print("\n-- C. Feature importance --")
    table, agree, cross, curve = run_feature_importance(
        X, y, classes, feature_columns, best_name, n_repeats, tables_dir, figures_dir
    )
    print(table[["feature", "final_f1_drop", "rf_f1_drop", "rf_mdi", "spearman_rho", "rank_final"]]
          .round(3).to_string(index=False))
    print("\n  Ranking agreement between methods:")
    print(agree.round(3).to_string(index=False))
    print("\n  Ma et al.'s four key attributes in our ranking:")
    print(cross.to_string(index=False))
    print("\n  How many lab tests are needed:")
    print(curve[["subset", "accuracy", "macro_f1", "features_most_often_chosen"]].round(2).to_string(index=False))
    return comp, head, table


def main():
    parser = argparse.ArgumentParser(description="Reproduce Ma et al. (2024) on the UCI red wine dataset.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help=f"use {QUICK_N_REPEATS} CV repeats instead of {N_REPEATS} for a fast sanity pass",
    )
    parser.add_argument(
        "--with-novelty",
        action="store_true",
        help="also run the optional Step 4 clustering / outlier / rule-mining extension",
    )
    parser.add_argument(
        "--review2",
        action="store_true",
        help="also run Review 2: class balancing, improvements and feature importance",
    )
    args = parser.parse_args()

    n_repeats = QUICK_N_REPEATS if args.quick else N_REPEATS

    # --quick runs a reduced protocol, so its output must NOT overwrite the
    # canonical 10-repeat results that README.md and report/methodology.md
    # quote. Send it to a scratch directory instead -- the same protection the
    # walkthrough notebook already uses.
    if args.quick:
        tables_dir = QUICK_OUTPUT_DIR
        figures_dir = QUICK_OUTPUT_DIR
        tables_dir.mkdir(parents=True, exist_ok=True)
    else:
        tables_dir, figures_dir = TABLES_DIR, FIGURES_DIR

    X, y, feature_columns, df = load_red_wine_xy()
    print(f"Loaded red wine dataset: {df.shape[0]} rows, {len(feature_columns)} features.")
    print(f"Protocol: 10-fold stratified CV x {n_repeats} repeats "
          f"({10 * n_repeats} total fold-runs).")
    if args.quick:
        print(f"QUICK MODE: reduced protocol -- output goes to {tables_dir}, "
              f"NOT to results/. The canonical results are left untouched.")
    print()

    _, baseline_all_results, _ = step3_reproduction(
        X, y, n_repeats, tables_dir=tables_dir, figures_dir=figures_dir
    )

    if args.with_novelty:
        if args.quick:
            print("\n(Skipping Step 4: the extension writes to results/ and would "
                  "overwrite canonical output. Run --with-novelty without --quick.)")
        else:
            step4_novelty(X, y, df, baseline_all_results, n_repeats)

    if args.review2:
        if args.quick:
            r2_tables, r2_figures = QUICK_REVIEW2_DIR / "tables", QUICK_REVIEW2_DIR / "figures"
        else:
            r2_tables, r2_figures = REVIEW2_TABLES_DIR, REVIEW2_FIGURES_DIR
        step5_review2(X, y, feature_columns, n_repeats, r2_tables, r2_figures)

    print("\n" + "=" * 72)
    if args.quick:
        print(f"DONE (quick mode). Output -> {tables_dir}")
    else:
        print("DONE. Tables -> results/tables/ , figures -> results/figures/")
    if args.review2:
        print("Review 2 -> " + str(QUICK_REVIEW2_DIR if args.quick else REVIEW2_TABLES_DIR.parent))
    else:
        print("(Review 2 skipped; pass --review2 to include it.)")
    if not args.with_novelty:
        print("(Step 4 extension skipped; pass --with-novelty to include it.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
