"""
preprocessing.py

Data loading and preprocessing for the UCI red wine quality dataset, matching
the preprocessing step in Ma et al. (2024) Fig. 2: raw data -> min-max
normalization -> downstream learners. No rows are dropped here; class 3/4/8
scarcity is handled explicitly downstream (stratified CV, balanced class
weights), not by discarding data.

WHERE THE SCALING HAPPENS: the min-max step now lives inside each learner's
Pipeline (see base_learners._pipe), so it is fit on the training fold only.
Use `load_red_wine_xy()` -- which returns RAW, unscaled X -- for anything that
feeds cross-validation. `load_normalized_red_wine()` is retained for standalone
inspection and for the optional novelty module, which fits unsupervised models
on the whole dataset at once (no train/test split, so no leakage concern).
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from config import FEATURE_COLUMNS, RED_WINE_CSV, TARGET_COLUMN

DEFAULT_RED_WINE_PATH = RED_WINE_CSV


def load_red_wine(path=DEFAULT_RED_WINE_PATH):
    """Load the red wine CSV (semicolon-delimited, as distributed by UCI)."""
    return pd.read_csv(path, sep=";")


def get_features_target(df, feature_columns=None):
    feature_columns = feature_columns or FEATURE_COLUMNS
    X = df[feature_columns].to_numpy(dtype=float)
    y = df[TARGET_COLUMN].to_numpy(dtype=int)
    return X, y


def minmax_normalize(X):
    """Min-max scale each feature to [0, 1] (paper's own preprocessing step)."""
    scaler = MinMaxScaler()
    X_norm = scaler.fit_transform(X)
    return X_norm, scaler


def train_test_split_data(X, y, test_size=0.2, random_state=42):
    """Stratified hold-out split, used only for the illustrative single-split
    metrics in base_learners.py. The paper's headline numbers (and ours, in
    ensemble.py) come from repeated k-fold CV, not this split."""
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )


def load_red_wine_xy(path=DEFAULT_RED_WINE_PATH, feature_columns=None):
    """Load the dataset and return RAW (unscaled) features.

    This is the loader every cross-validated experiment should use: scaling is
    applied inside each learner's Pipeline, fit on the training fold only.

    Returns (X_raw, y, feature_columns, df).
    """
    df = load_red_wine(path)
    feature_columns = feature_columns or FEATURE_COLUMNS
    X, y = get_features_target(df, feature_columns)
    return X, y, feature_columns, df


def load_normalized_red_wine(path=DEFAULT_RED_WINE_PATH, feature_columns=None):
    """Convenience wrapper: load -> extract features/target -> min-max normalize.

    NOTE: scales using the whole dataset. Safe for unsupervised analysis over
    all rows at once (the optional novelty module), but do NOT feed the result
    into cross-validation -- use `load_red_wine_xy()` for that instead.

    Returns (X_norm, y, feature_columns, df).
    """
    df = load_red_wine(path)
    feature_columns = feature_columns or FEATURE_COLUMNS
    X, y = get_features_target(df, feature_columns)
    X_norm, _ = minmax_normalize(X)
    return X_norm, y, feature_columns, df


if __name__ == "__main__":
    df = load_red_wine()
    print("shape:", df.shape)
    print(df.head())
    print("\nquality value_counts:")
    print(df[TARGET_COLUMN].value_counts().sort_index())

    X, y = get_features_target(df)
    X_norm, _ = minmax_normalize(X)
    print("\nnormalized feature range check (min, max) per column:")
    print(np.round(X_norm.min(axis=0), 3))
    print(np.round(X_norm.max(axis=0), 3))
