"""
novelty_cluster_mine_feedback.py

Novelty extension targeting Ma et al. (2024)'s own stated limitation: poor
precision on the extreme quality classes (3, 4, 8), which the paper attributes
to small sample size. Four parts:

  4a. Unsupervised clustering (K-means + Ward's linkage agglomerative) on the
      11 physicochemical features only (no quality label). k = 3..8, best k
      chosen by silhouette score. Cross-tabulated against actual quality
      class to see whether clusters found from attributes alone line up with
      quality tiers.
  4b. Outlier detection (Isolation Forest + Local Outlier Factor). Checks
      whether classes 3/4/8 are flagged as outliers at a higher rate than the
      well-represented classes 5/6/7 -- i.e. whether "small sample" also means
      "genuinely atypical," not just "few."
  4c. Feed the best clustering's cluster ID back into the Step-3 ensemble as a
      12th input feature; compare per-class precision with vs. without it,
      especially for classes 3, 4, 8.
  4d. Frequent pattern mining (fpgrowth + association_rules) on a
      Low(3,4)/High(7,8) quality-tier split (Medium 5,6 dropped for cleaner,
      higher-lift rules), run on the whole dataset and separately within each
      cluster from 4a. Rules are filtered to consequent = "quality=High",
      sorted by lift, and cross-checked against the attributes Ma et al.
      (2024) Figs. 4-5 flag as most important (alcohol, sulphates, volatile
      acidity, citric acid).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mlxtend.frequent_patterns import association_rules, fpgrowth
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.neighbors import LocalOutlierFactor

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"

RANDOM_STATE = 42
K_RANGE = range(3, 9)
CONTAMINATION = 0.10
FIG4_5_KEY_ATTRIBUTES = {"alcohol", "sulphates", "volatile acidity", "citric acid"}


# ---------------------------------------------------------------------------
# 4a. Clustering
# ---------------------------------------------------------------------------
def run_clustering(X, k_range=K_RANGE, random_state=RANDOM_STATE):
    """K-means and Ward agglomerative clustering over k_range; silhouette
    score for each; returns the best (method, k, labels) by silhouette."""
    rows = []
    labels_by_method_k = {}

    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        km_labels = km.fit_predict(X)
        rows.append({"method": "kmeans", "k": k, "silhouette": silhouette_score(X, km_labels)})
        labels_by_method_k[("kmeans", k)] = km_labels

        ward = AgglomerativeClustering(n_clusters=k, linkage="ward")
        ward_labels = ward.fit_predict(X)
        rows.append({"method": "ward", "k": k, "silhouette": silhouette_score(X, ward_labels)})
        labels_by_method_k[("ward", k)] = ward_labels

    silhouette_df = pd.DataFrame(rows)
    best_row = silhouette_df.loc[silhouette_df["silhouette"].idxmax()]
    best_method, best_k = best_row["method"], int(best_row["k"])
    best_labels = labels_by_method_k[(best_method, best_k)]

    return {
        "silhouette_df": silhouette_df,
        "best_method": best_method,
        "best_k": best_k,
        "best_labels": best_labels,
        "labels_by_method_k": labels_by_method_k,
    }


def cluster_quality_crosstab(cluster_labels, y):
    return pd.crosstab(
        pd.Series(cluster_labels, name="cluster"), pd.Series(y, name="quality_class")
    )


def save_clustering_outputs(clustering_result, y, tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    clustering_result["silhouette_df"].to_csv(tables_dir / "clustering_silhouette_scores.csv", index=False)

    crosstab = cluster_quality_crosstab(clustering_result["best_labels"], y)
    crosstab.to_csv(tables_dir / "cluster_quality_crosstab.csv")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(crosstab, annot=True, fmt="d", cmap="viridis", ax=ax)
    ax.set_title(
        f"Cluster vs. quality class "
        f"(best: {clustering_result['best_method']}, k={clustering_result['best_k']})"
    )
    fig.tight_layout()
    fig.savefig(figures_dir / "cluster_quality_heatmap.png", dpi=150)
    plt.close(fig)

    return crosstab


# ---------------------------------------------------------------------------
# 4b. Outlier detection
# ---------------------------------------------------------------------------
def run_outlier_detection(X, y, contamination=CONTAMINATION, random_state=RANDOM_STATE):
    iso = IsolationForest(contamination=contamination, random_state=random_state)
    iso_outlier = iso.fit_predict(X) == -1

    lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
    lof_outlier = lof.fit_predict(X) == -1

    per_sample = pd.DataFrame(
        {"quality_class": y, "isolation_forest_outlier": iso_outlier, "lof_outlier": lof_outlier}
    )
    rate_by_class = (
        per_sample.groupby("quality_class")[["isolation_forest_outlier", "lof_outlier"]].mean() * 100
    )
    rate_by_class.columns = ["isolation_forest_outlier_pct", "lof_outlier_pct"]
    return per_sample, rate_by_class


def save_outlier_outputs(rate_by_class, tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    rate_by_class.to_csv(tables_dir / "outlier_rates_by_class.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    rate_by_class.plot(kind="bar", ax=ax)
    ax.set_xlabel("Quality class")
    ax.set_ylabel("Outlier rate (%)")
    ax.set_title("Outlier rate by quality class (extreme classes 3/4/8 vs. 5/6/7)")
    ax.legend(["Isolation Forest", "Local Outlier Factor"])
    fig.tight_layout()
    fig.savefig(figures_dir / "outlier_rate_by_class.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4c. Feedback into the classifier
# ---------------------------------------------------------------------------
def augment_with_cluster_feature(X, cluster_labels, n_clusters):
    """Append cluster id as a 12th feature, min-max scaled to [0, 1] to match
    the scale of the other (already min-max normalized) features."""
    denom = max(n_clusters - 1, 1)
    cluster_feature = (np.asarray(cluster_labels, dtype=float) / denom).reshape(-1, 1)
    return np.hstack([X, cluster_feature])


def compare_cluster_feedback(metrics_without, metrics_with, classes_of_interest=(3, 4, 8)):
    """Compare per-class "precision" (paper definition = recall) with vs.
    without the cluster-ID feature, for the given classes of interest."""
    without = metrics_without.set_index("class")["precision_paper_definition_pct"]
    with_ = metrics_with.set_index("class")["precision_paper_definition_pct"]
    all_classes = sorted(set(without.index) | set(with_.index))

    comparison = pd.DataFrame(
        {
            "class": all_classes,
            "precision_without_cluster_feature_pct": [without.get(c, np.nan) for c in all_classes],
            "precision_with_cluster_feature_pct": [with_.get(c, np.nan) for c in all_classes],
        }
    )
    comparison["delta_pct"] = (
        comparison["precision_with_cluster_feature_pct"] - comparison["precision_without_cluster_feature_pct"]
    )
    comparison["is_extreme_class_of_interest"] = comparison["class"].isin(classes_of_interest)
    return comparison


def save_cluster_feedback_outputs(comparison_df, tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(tables_dir / "cluster_feedback_precision_comparison.csv", index=False)

    labels = [str(c) for c in comparison_df["class"]]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, comparison_df["precision_without_cluster_feature_pct"], width, label="Without cluster ID")
    ax.bar(x + width / 2, comparison_df["precision_with_cluster_feature_pct"], width, label="With cluster ID")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Quality class")
    ax.set_ylabel("Precision (paper definition = recall) (%)")
    ax.set_title("Ensemble per-class precision: before vs. after cluster-ID feedback feature")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "cluster_feedback_precision_comparison.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4d. Frequent pattern mining
# ---------------------------------------------------------------------------
def discretize_features(raw_feature_df, feature_columns, n_bins=3, bin_labels=("Low", "Med", "High")):
    """Discretize each continuous feature into `n_bins` quantile bins."""
    discretized = pd.DataFrame(index=raw_feature_df.index)
    for col in feature_columns:
        try:
            binned = pd.qcut(raw_feature_df[col], q=n_bins, labels=bin_labels[:n_bins], duplicates="drop")
        except ValueError:
            # Too many repeated values for `n_bins` distinct quantile edges;
            # fall back to ranking first so every row still gets a bin.
            binned = pd.qcut(raw_feature_df[col].rank(method="first"), q=n_bins, labels=bin_labels[:n_bins])
        discretized[col] = binned.astype(str)
    return discretized


def compute_quality_tier(y):
    """Low = classes 3-4, High = classes 7-8, Medium (5-6) is dropped later
    for cleaner, higher-lift rules -- both dropped classes are the
    best-represented and least in need of extra scrutiny here."""
    tier = np.full(len(y), "Medium", dtype=object)
    tier[np.isin(y, [3, 4])] = "Low"
    tier[np.isin(y, [7, 8])] = "High"
    return tier


def _one_hot_items(discretized_df):
    items = pd.DataFrame(index=discretized_df.index)
    for col in discretized_df.columns:
        dummies = pd.get_dummies(discretized_df[col], prefix=col, prefix_sep="=")
        items = pd.concat([items, dummies], axis=1)
    return items


def build_basket(discretized_df, tier, row_mask):
    sub_disc = discretized_df.loc[row_mask]
    sub_tier = pd.Series(np.asarray(tier)[row_mask], index=sub_disc.index)
    items = _one_hot_items(sub_disc)
    tier_dummies = pd.get_dummies(sub_tier, prefix="quality", prefix_sep="=")
    basket = pd.concat([items, tier_dummies], axis=1).fillna(False).astype(bool)
    return basket


def mine_rules(basket, min_support=0.05):
    if basket.shape[0] == 0:
        return pd.DataFrame()
    freq_items = fpgrowth(basket, min_support=min_support, use_colnames=True)
    if freq_items.empty:
        return pd.DataFrame()
    return association_rules(freq_items, num_itemsets=len(basket), metric="lift", min_threshold=1.0)


def filter_high_quality_rules(rules, top_n=10):
    if rules.empty:
        return rules
    mask = rules["consequents"].apply(lambda s: set(s) == {"quality=High"})
    return rules.loc[mask].sort_values("lift", ascending=False).head(top_n)


def rule_antecedent_attributes(rules_df):
    attrs = set()
    for antecedents in rules_df.get("antecedents", []):
        for item in antecedents:
            attrs.add(item.split("=")[0])
    return attrs


def run_frequent_pattern_mining(
    raw_feature_df, feature_columns, y, cluster_labels, n_bins=3, min_support=0.05, min_cluster_rows=10
):
    discretized_df = discretize_features(raw_feature_df, feature_columns, n_bins)
    tier = compute_quality_tier(y)
    low_high_mask = tier != "Medium"

    basket_full = build_basket(discretized_df, tier, low_high_mask)
    rules_full = mine_rules(basket_full, min_support=min_support)
    top10_overall = filter_high_quality_rules(rules_full, top_n=10)

    per_cluster_top5 = {}
    for cluster_id in sorted(np.unique(cluster_labels)):
        cluster_mask = low_high_mask & (np.asarray(cluster_labels) == cluster_id)
        if cluster_mask.sum() < min_cluster_rows:
            per_cluster_top5[cluster_id] = pd.DataFrame()
            continue
        basket_c = build_basket(discretized_df, tier, cluster_mask)
        rules_c = mine_rules(basket_c, min_support=min_support)
        per_cluster_top5[cluster_id] = filter_high_quality_rules(rules_c, top_n=5)

    return top10_overall, per_cluster_top5


def crosscheck_with_paper_figures(top10_overall):
    mined_attrs = rule_antecedent_attributes(top10_overall)
    agree = mined_attrs & FIG4_5_KEY_ATTRIBUTES
    disagree_mined_only = mined_attrs - FIG4_5_KEY_ATTRIBUTES
    disagree_paper_only = FIG4_5_KEY_ATTRIBUTES - mined_attrs
    return {
        "mined_attributes": mined_attrs,
        "paper_key_attributes": FIG4_5_KEY_ATTRIBUTES,
        "agreement": agree,
        "mined_only": disagree_mined_only,
        "paper_only": disagree_paper_only,
    }


def _rules_to_readable(rules_df):
    if rules_df.empty:
        return rules_df
    out = rules_df.copy()
    out["antecedents"] = out["antecedents"].apply(lambda s: ", ".join(sorted(s)))
    out["consequents"] = out["consequents"].apply(lambda s: ", ".join(sorted(s)))
    keep_cols = ["antecedents", "consequents", "support", "confidence", "lift"]
    return out[keep_cols]


def save_mining_outputs(top10_overall, per_cluster_top5, crosscheck, tables_dir=TABLES_DIR, figures_dir=FIGURES_DIR):
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    readable_overall = _rules_to_readable(top10_overall)
    readable_overall.to_csv(tables_dir / "top_association_rules_overall.csv", index=False)

    per_cluster_frames = []
    for cluster_id, rules_df in per_cluster_top5.items():
        readable = _rules_to_readable(rules_df)
        readable = readable.copy()
        readable.insert(0, "cluster", cluster_id)
        per_cluster_frames.append(readable)
    per_cluster_combined = (
        pd.concat(per_cluster_frames, ignore_index=True) if per_cluster_frames else pd.DataFrame()
    )
    per_cluster_combined.to_csv(tables_dir / "top_association_rules_per_cluster.csv", index=False)

    # Markdown + image renderings of the overall top-10 table (deliverable
    # asks for the rules "as image or markdown table").
    md_path = figures_dir / "top_association_rules.md"
    with open(md_path, "w") as f:
        f.write("# Top 10 association rules for quality=High (overall, sorted by lift)\n\n")
        f.write(readable_overall.round(4).to_markdown(index=False) if not readable_overall.empty else "_No rules found at this support threshold._\n")
        f.write("\n\n## Cross-check against Ma et al. (2024) Figs. 4-5 key attributes\n\n")
        f.write(f"- Attributes appearing in our mined rules: {sorted(crosscheck['mined_attributes'])}\n")
        f.write(f"- Paper's flagged key attributes (alcohol, sulphates, volatile acidity, citric acid): {sorted(crosscheck['paper_key_attributes'])}\n")
        f.write(f"- Agreement: {sorted(crosscheck['agreement'])}\n")
        f.write(f"- In our rules only: {sorted(crosscheck['mined_only'])}\n")
        f.write(f"- In paper's figures only, not in our top rules: {sorted(crosscheck['paper_only'])}\n")

    if not readable_overall.empty:
        fig, ax = plt.subplots(figsize=(12, 0.5 + 0.4 * len(readable_overall)))
        ax.axis("off")
        table_data = readable_overall.round(3).values
        tbl = ax.table(
            cellText=table_data,
            colLabels=readable_overall.columns,
            loc="center",
            cellLoc="left",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.auto_set_column_width(list(range(len(readable_overall.columns))))
        ax.set_title("Top 10 association rules for quality=High (overall, by lift)", pad=20)
        fig.tight_layout()
        fig.savefig(figures_dir / "top_association_rules.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    from evaluate import per_class_metrics
    from ensemble import run_repeated_cv
    from preprocessing import FEATURE_COLUMNS, load_normalized_red_wine

    X, y, feature_columns, df = load_normalized_red_wine()

    print("Running clustering (4a)...")
    clustering_result = run_clustering(X)
    print(f"Best clustering: {clustering_result['best_method']} k={clustering_result['best_k']}")
    save_clustering_outputs(clustering_result, y)

    print("Running outlier detection (4b)...")
    _, rate_by_class = run_outlier_detection(X, y)
    save_outlier_outputs(rate_by_class)
    print(rate_by_class)

    print("Running cluster-feedback ensemble comparison (4c, quick 2-repeat smoke test)...")
    baseline_results = run_repeated_cv(X, y, n_repeats=2)
    baseline_metrics = per_class_metrics(
        baseline_results["pooled_true"], baseline_results["pooled_ensemble"], baseline_results["classes"]
    )
    X_aug = augment_with_cluster_feature(X, clustering_result["best_labels"], clustering_result["best_k"])
    aug_results = run_repeated_cv(X_aug, y, n_repeats=2)
    aug_metrics = per_class_metrics(
        aug_results["pooled_true"], aug_results["pooled_ensemble"], aug_results["classes"]
    )
    comparison = compare_cluster_feedback(baseline_metrics, aug_metrics)
    save_cluster_feedback_outputs(comparison)
    print(comparison)

    print("Running frequent pattern mining (4d)...")
    top10, per_cluster = run_frequent_pattern_mining(df, FEATURE_COLUMNS, y, clustering_result["best_labels"])
    crosscheck = crosscheck_with_paper_figures(top10)
    save_mining_outputs(top10, per_cluster, crosscheck)
    print(crosscheck)
