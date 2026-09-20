"""
=================================================================================
Water Quality Index (WQI) Prediction Pipeline
=================================================================================
ML-based WQI Classification & Prediction using Transfer Learning
From Jalaur River System (JRS-WQMA) 2020-2025 Regional Data

Dataset : WQMA_JRS_2020_2025.csv (converted from EMB Region 6 PDF)
Source   : 10 Stations, 6 Years, Monthly Monitoring

Methodology (Proposal Paper):
  1. WQI Computation   - Weighted Arithmetic Water Quality Index (DENR DAO 2016-08)
  2. Data Preprocessing - KNN Imputation + Isolation Forest Outlier Detection
  3. Feature Engineering - Entropy Weighting + Pearson Correlation
  4. WQI Classification - DENR-Standardized Suitability Classes
  5. ML Training        - XGBoost, SVM (RBF), Multilayer Perceptron
  6. Evaluation         - Accuracy, Precision, Recall, F1, R2
  7. Model Export       - Saved for Streamlit Deployment
=================================================================================
"""

import os
import sys
import io
import warnings
import numpy as np
import pandas as pd

# Fix Windows cp1252 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy as scipy_entropy

from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    r2_score,
    ConfusionMatrixDisplay,
)
import xgboost as xgb
import joblib

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# -----------------------------------------------
# PATHS
# -----------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODEL_DIR = os.path.join(OUTPUT_DIR, "models")
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

INPUT_CSV = os.path.join(DATA_DIR, "WQMA_JRS_2020_2025.csv")

# Physicochemical features available from WQMA data
FEATURE_COLS = ["DO", "BOD", "TSS", "pH", "Temperature", "Fecal_Coliform"]

# Field-deployable features (portable meter readings only) + Engineered features
FIELD_FEATURES = ["pH", "DO", "Temperature", "DO_Temp_Ratio", "pH_Deviation"]

# All features for training (including lab features)
TRAINING_FEATURES = FEATURE_COLS + ["DO_Temp_Ratio", "pH_Deviation"]

# -----------------------------------------------
# DENR DAO 2016-08 Standards for WQI Computation
# -----------------------------------------------
# Standard ideal values (Si) and permissible values for each parameter
# Based on DENR DAO 2016-08 Class C (Fishery Water)
DENR_STANDARDS = {
    "DO":              {"Si": 5.0,   "ideal": 14.6, "unit": "mg/L",     "weight": 0.1968},
    "BOD":             {"Si": 7.0,   "ideal": 0.0,  "unit": "mg/L",     "weight": 0.1311},
    "TSS":             {"Si": 80.0,  "ideal": 0.0,  "unit": "mg/L",     "weight": 0.0656},
    "pH":              {"Si": 9.0,   "ideal": 7.0,  "unit": "",         "weight": 0.1311},
    "Temperature":     {"Si": 31.0,  "ideal": 25.0, "unit": "C",        "weight": 0.0656},
    "Fecal_Coliform":  {"Si": 200.0, "ideal": 0.0,  "unit": "MPN/100mL","weight": 0.4098},
}


# =============================================================================
# 1. LOAD DATA
# =============================================================================
def load_data(path):
    print("=" * 70)
    print("STEP 1: LOADING WQMA DATA")
    print("=" * 70)
    df = pd.read_csv(path)
    print(f"  Source   : {os.path.basename(path)}")
    print(f"  Shape    : {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Years    : {sorted(df['Year'].unique())}")
    print(f"  Stations : {df['Station_ID'].nunique()}")
    print(f"  Missing  :")
    for col in df.columns:
        n = df[col].isnull().sum()
        if n > 0:
            print(f"    {col:20s}: {n} nulls")
    return df


# =============================================================================
# 2. DATA PREPROCESSING - KNN Imputation + Outlier Detection
# =============================================================================
def preprocess_data(df):
    print("\n" + "=" * 70)
    print("STEP 2: DATA PREPROCESSING")
    print("=" * 70)

    # Drop columns with too many nulls (Phosphate: 600/700 null)
    drop_cols = ["Phosphate", "PO4_P", "Color_TCU"]
    existing_drop = [c for c in drop_cols if c in df.columns]
    if existing_drop:
        print(f"\n  Dropping sparse columns: {existing_drop}")
        df = df.drop(columns=existing_drop)

    # --- 2a. KNN Imputation for pH (20 nulls) ---
    print("\n  [2a] KNN Imputation (k=5) for missing pH values...")
    missing_before = df[FEATURE_COLS].isnull().sum().sum()
    imputer = KNNImputer(n_neighbors=5, metric="nan_euclidean")
    df[FEATURE_COLS] = pd.DataFrame(
        imputer.fit_transform(df[FEATURE_COLS]),
        columns=FEATURE_COLS,
        index=df.index,
    )
    missing_after = df[FEATURE_COLS].isnull().sum().sum()
    print(f"       Missing values: {missing_before} -> {missing_after}")

    # --- 2b. Isolation Forest Outlier Detection ---
    print("\n  [2b] Isolation Forest Outlier Detection...")
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )
    outlier_labels = iso_forest.fit_predict(df[FEATURE_COLS])
    n_outliers = (outlier_labels == -1).sum()
    print(f"       Detected outliers : {n_outliers} / {len(df)}")

    df_clean = df[outlier_labels == 1].reset_index(drop=True)
    print(f"       Clean dataset     : {df_clean.shape[0]} rows retained")

    # --- 2c. Feature Engineering (Field Ratios) ---
    print("\n  [2c] Computing engineered field features...")
    df_clean["DO_Temp_Ratio"] = df_clean["DO"] / df_clean["Temperature"]
    df_clean["pH_Deviation"] = (df_clean["pH"] - 7.0).abs()
    
    return df_clean


# =============================================================================
# 3. WQI COMPUTATION - Weighted Arithmetic Method (DENR DAO 2016-08)
# =============================================================================
def compute_quality_rating(value, param):
    """
    Compute quality rating (qi) for a parameter.
    qi = ((Vi - V_ideal) / (Si - V_ideal)) * 100
    where Vi = observed value, Si = standard value, V_ideal = ideal value
    """
    std = DENR_STANDARDS[param]
    si = std["Si"]
    ideal = std["ideal"]

    if si == ideal:
        return 0

    qi = ((value - ideal) / (si - ideal)) * 100
    return max(qi, 0)  # Clamp to 0 minimum


def compute_wqi(row):
    """
    Compute Weighted Arithmetic WQI for a single row.
    WQI = SUM(qi * wi) / SUM(wi)
    """
    numerator = 0
    denominator = 0

    for param in FEATURE_COLS:
        if param not in DENR_STANDARDS:
            continue
        value = row[param]
        if pd.isna(value):
            continue

        qi = compute_quality_rating(value, param)
        wi = DENR_STANDARDS[param]["weight"]

        numerator += qi * wi
        denominator += wi

    if denominator == 0:
        return np.nan

    return numerator / denominator


def compute_wqi_column(df):
    print("\n" + "=" * 70)
    print("STEP 3: WQI COMPUTATION (Weighted Arithmetic Method)")
    print("=" * 70)

    print("\n  DENR DAO 2016-08 Standards & Weights:")
    print(f"  {'Parameter':20s} {'Standard':>10s} {'Ideal':>10s} {'Weight':>10s}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
    for param, std in DENR_STANDARDS.items():
        print(f"  {param:20s} {std['Si']:>10.1f} {std['ideal']:>10.1f} {std['weight']:>10.4f}")

    print(f"\n  Formula: WQI = SUM(qi x wi) / SUM(wi)")
    print(f"  where qi = ((Vi - V_ideal) / (Si - V_ideal)) x 100")

    df["WQI"] = df.apply(compute_wqi, axis=1)

    print(f"\n  WQI Statistics:")
    print(f"    Mean  : {df['WQI'].mean():.2f}")
    print(f"    Median: {df['WQI'].median():.2f}")
    print(f"    Min   : {df['WQI'].min():.2f}")
    print(f"    Max   : {df['WQI'].max():.2f}")
    print(f"    Std   : {df['WQI'].std():.2f}")

    # Plot WQI distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df["WQI"], bins=40, color="#3498db", edgecolor="white", alpha=0.85)
    axes[0].set_xlabel("WQI Score")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("WQI Distribution (JRS-WQMA 2020-2025)")
    axes[0].axvline(25, color='green', ls='--', lw=1.5, label='Excellent/Good')
    axes[0].axvline(50, color='orange', ls='--', lw=1.5, label='Good/Poor')
    axes[0].axvline(75, color='red', ls='--', lw=1.5, label='Poor/Very Poor')
    axes[0].axvline(100, color='darkred', ls='--', lw=1.5, label='Very Poor/Unsuitable')
    axes[0].legend(fontsize=8)

    # WQI by station
    station_wqi = df.groupby("Station_Name")["WQI"].mean().sort_values()
    axes[1].barh(range(len(station_wqi)), station_wqi.values, color="#2ecc71", edgecolor="white")
    axes[1].set_yticks(range(len(station_wqi)))
    axes[1].set_yticklabels([n[:25] for n in station_wqi.index], fontsize=8)
    axes[1].set_xlabel("Mean WQI")
    axes[1].set_title("Average WQI by Station")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "wqi_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: wqi_distribution.png")

    return df


# =============================================================================
# 4. FEATURE ENGINEERING - Entropy + Pearson Weighting
# =============================================================================
def compute_feature_weights(df):
    print("\n" + "=" * 70)
    print("STEP 4: FEATURE ENGINEERING - Comprehensive Weighting")
    print("=" * 70)

    features = df[FEATURE_COLS]
    target = df["WQI"]

    # Entropy Weighting
    feat_norm = (features - features.min()) / (features.max() - features.min() + 1e-10)
    entropy_weights = {}
    for col in FEATURE_COLS:
        hist, _ = np.histogram(feat_norm[col].dropna(), bins=20, density=True)
        hist = hist / hist.sum() if hist.sum() > 0 else hist
        hist = hist[hist > 0]
        ent = scipy_entropy(hist, base=2)
        entropy_weights[col] = ent

    max_ent = max(entropy_weights.values()) if max(entropy_weights.values()) > 0 else 1
    entropy_weights = {k: v / max_ent for k, v in entropy_weights.items()}

    # Pearson Correlation
    pearson_weights = {}
    for col in FEATURE_COLS:
        corr = features[col].corr(target)
        pearson_weights[col] = abs(corr)

    # Combined
    weight_df = pd.DataFrame({
        "Feature": FEATURE_COLS,
        "Entropy_Weight": [entropy_weights[c] for c in FEATURE_COLS],
        "Pearson_Corr": [pearson_weights[c] for c in FEATURE_COLS],
    })
    weight_df["Combined_Weight"] = weight_df["Entropy_Weight"] * weight_df["Pearson_Corr"]
    weight_df["Normalized_Weight"] = weight_df["Combined_Weight"] / weight_df["Combined_Weight"].sum()
    weight_df = weight_df.sort_values("Normalized_Weight", ascending=False)
    print(f"\n{weight_df.to_string(index=False)}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].barh(weight_df["Feature"], weight_df["Entropy_Weight"], color="#4C72B0")
    axes[0].set_title("Entropy Weights")
    axes[1].barh(weight_df["Feature"], weight_df["Pearson_Corr"], color="#DD8452")
    axes[1].set_title("|Pearson Correlation| with WQI")
    axes[2].barh(weight_df["Feature"], weight_df["Normalized_Weight"], color="#55A868")
    axes[2].set_title("Combined Normalized Weights")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "feature_weights.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: feature_weights.png")

    return weight_df


# =============================================================================
# 5. WQI CLASSIFICATION - DENR Suitability Classes
# =============================================================================
def assign_wqi_class(wqi_value):
    """
    WQI Range    | Class       | DENR Suitability
    0 - 25       | Excellent   | Class AA (Public Water Supply I)
    26 - 50      | Good        | Class A  (Public Water Supply II)
    51 - 75      | Poor        | Class B  (Recreational)
    76 - 100     | Very_Poor   | Class C  (Fishery/Industrial)
    > 100        | High Risk   | Class D  (Agriculture/Navigation)
    """
    if wqi_value <= 25:
        return "Excellent"
    elif wqi_value <= 50:
        return "Good"
    elif wqi_value <= 75:
        return "Poor"
    elif wqi_value <= 100:
        return "Very_Poor"
    else:
        return "High Risk"


def create_classification_target(df):
    print("\n" + "=" * 70)
    print("STEP 5: WQI CLASSIFICATION (DENR Suitability)")
    print("=" * 70)

    df["WQI_Class"] = df["WQI"].apply(assign_wqi_class)

    class_dist = df["WQI_Class"].value_counts()
    print("\n  Class Distribution:")
    for cls, count in class_dist.items():
        pct = count / len(df) * 100
        print(f"    {cls:15s} : {count:4d}  ({pct:5.1f}%)")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"Excellent": "#2ecc71", "Good": "#3498db", "Poor": "#f39c12",
              "Very_Poor": "#e74c3c", "High Risk": "#8e44ad"}
    order = ["Excellent", "Good", "Poor", "Very_Poor", "High Risk"]
    existing = [c for c in order if c in class_dist.index]
    bars = ax.bar(existing, [class_dist[c] for c in existing],
                  color=[colors[c] for c in existing], edgecolor="white", linewidth=1.5)
    for bar, cls in zip(bars, existing):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(class_dist[cls]), ha="center", fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_title("WQI Suitability Class Distribution (JRS-WQMA 2020-2025)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "wqi_class_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: wqi_class_distribution.png")

    return df


# =============================================================================
# 6. CORRELATION HEATMAP
# =============================================================================
def plot_correlation_heatmap(df):
    print("\n  Generating correlation heatmap...")
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_matrix = df[FEATURE_COLS + ["WQI"]].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0, square=True, linewidths=0.5, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Matrix (JRS-WQMA 2020-2025)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "correlation_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: correlation_heatmap.png")


# =============================================================================
# 7. MODEL TRAINING & EVALUATION
# =============================================================================
def train_and_evaluate(df):
    print("\n" + "=" * 70)
    print("STEP 6: MODEL TRAINING & EVALUATION (All Features)")
    print("=" * 70)

    X = df[TRAINING_FEATURES].copy()
    y_labels = df["WQI_Class"].copy()

    le = LabelEncoder()
    y_encoded = le.fit_transform(y_labels)
    class_names = le.classes_

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # Balance dataset with SMOTE on training data only
    print("\n  Balancing training dataset using SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=1) # k=1 because some classes only have 2 samples
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    print("  Class distribution before SMOTE:")
    before_counts = pd.Series(y_train).value_counts().sort_index()
    for cls_idx, count in before_counts.items():
        print(f"    {class_names[cls_idx]:15s} : {count}")
        
    print("  Class distribution after SMOTE:")
    after_counts = pd.Series(y_train_resampled).value_counts().sort_index()
    for cls_idx, count in after_counts.items():
        print(f"    {class_names[cls_idx]:15s} : {count}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        "XGBoost": {
            "estimator": xgb.XGBClassifier(
                objective="multi:softmax", eval_metric="mlogloss",
                use_label_encoder=False, random_state=42, verbosity=0,
            ),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.05, 0.1, 0.2],
                "subsample": [0.8, 1.0],
            },
        },
        "SVM": {
            "estimator": SVC(random_state=42, probability=True),
            "params": {
                "C": [0.1, 1, 10, 100],
                "gamma": ["scale", "auto", 0.01, 0.1],
                "kernel": ["rbf"],
            },
        },
        "MLP": {
            "estimator": MLPClassifier(
                random_state=42, max_iter=1000, early_stopping=True,
                validation_fraction=0.15,
            ),
            "params": {
                "hidden_layer_sizes": [(64, 32), (128, 64), (100, 50, 25)],
                "activation": ["relu", "tanh"],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate": ["constant", "adaptive"],
            },
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(random_state=42, n_jobs=1),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [None, 5, 10],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 2],
            }
        },
    }

    results = {}
    best_models = {}

    for name, config in models.items():
        print(f"\n  -- Training: {name} --")
        print(f"     Grid Search with 5-Fold Stratified CV on Training Set (80%)...")

        grid = GridSearchCV(
            estimator=config["estimator"], param_grid=config["params"],
            cv=skf, scoring="f1_weighted", n_jobs=1, verbose=1, refit=True,
        )
        grid.fit(X_train_resampled, y_train_resampled)

        best_model = grid.best_estimator_
        best_models[name] = best_model

        print(f"     Best Params : {grid.best_params_}")
        print(f"     Best CV F1  : {grid.best_score_:.4f}")

        # Evaluate on the 20% validation set
        y_pred = best_model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        r2 = r2_score(y_test, y_pred)

        results[name] = {"Accuracy": acc, "Precision": prec, "Recall": rec,
                         "F1_Score": f1, "R2": r2}

        print(f"\n     +------------------------------------+")
        print(f"     | {name:^34s} |")
        print(f"     +--------------+-------------------+")
        print(f"     | Accuracy     | {acc:>17.4f} |")
        print(f"     | Precision    | {prec:>17.4f} |")
        print(f"     | Recall       | {rec:>17.4f} |")
        print(f"     | F1-Score     | {f1:>17.4f} |")
        print(f"     | R2           | {r2:>17.4f} |")
        print(f"     +--------------+-------------------+")

        y_test_labels = le.inverse_transform(y_test)
        y_pred_labels = le.inverse_transform(y_pred)
        print(f"\n     Classification Report ({name} on 20% Test):")
        print(classification_report(y_test_labels, y_pred_labels, zero_division=0))

        cm = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(8, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
        disp.plot(ax=ax, cmap="Blues", values_format="d")
        ax.set_title(f"Confusion Matrix - {name}")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, f"confusion_matrix_{name.lower()}.png"),
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"     -> Saved: confusion_matrix_{name.lower()}.png")

        model_path = os.path.join(MODEL_DIR, f"{name.lower()}_model.pkl")
        joblib.dump(best_model, model_path)
        print(f"     -> Model saved: {model_path}")

    # Save scaler & encoder
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    joblib.dump(le, os.path.join(MODEL_DIR, "label_encoder.pkl"))
    print(f"\n  -> Scaler saved : {os.path.join(MODEL_DIR, 'scaler.pkl')}")
    print(f"  -> Encoder saved: {os.path.join(MODEL_DIR, 'label_encoder.pkl')}")

    return results, best_models


# =============================================================================
# 8. MODEL COMPARISON
# =============================================================================
def summarize_results(results):
    print("\n" + "=" * 70)
    print("STEP 7: MODEL COMPARISON SUMMARY")
    print("=" * 70)

    results_df = pd.DataFrame(results).T
    results_df.index.name = "Model"
    print(f"\n{results_df.round(4).to_string()}\n")

    best_model_name = results_df["F1_Score"].idxmax()
    best_f1 = results_df.loc[best_model_name, "F1_Score"]
    print(f"  * Best Model: {best_model_name} (F1 = {best_f1:.4f})")

    fig, ax = plt.subplots(figsize=(12, 6))
    results_df[["Accuracy", "Precision", "Recall", "F1_Score", "R2"]].plot(
        kind="bar", ax=ax, width=0.7,
        color=["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"],
        edgecolor="white", linewidth=1.2,
    )
    ax.set_title("Model Performance Comparison", fontsize=14, fontweight="bold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", framealpha=0.9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=8, padding=2)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "model_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: model_comparison.png")

    results_csv = os.path.join(OUTPUT_DIR, "model_results.csv")
    results_df.to_csv(results_csv)
    print(f"  -> Saved: {results_csv}")

    return results_df


# =============================================================================
# 9. FIELD DEPLOYMENT SIMULATION
# =============================================================================
def simulate_field_prediction(best_models):
    print("\n" + "=" * 70)
    print("STEP 8: FIELD DEPLOYMENT SIMULATION")
    print("=" * 70)

    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    le = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

    print("\n  NOTE: In deployment, the web app will require ALL 6 parameters.")
    print("  Models were trained on full lab features + engineered features.\n")

    sample_readings = pd.DataFrame([
        {"pH": 7.8, "DO": 7.5, "Temperature": 27.0, "BOD": 2.0, "TSS": 112.0, "Fecal_Coliform": 140.0},
        {"pH": 7.3, "DO": 5.2, "Temperature": 25.5, "BOD": 4.5, "TSS": 90.0, "Fecal_Coliform": 14000.0},
        {"pH": 8.1, "DO": 8.8, "Temperature": 22.0, "BOD": 1.2, "TSS": 45.0, "Fecal_Coliform": 50.0},
        {"pH": 6.5, "DO": 3.0, "Temperature": 30.0, "BOD": 8.0, "TSS": 200.0, "Fecal_Coliform": 85000.0},
    ])
    
    # Compute engineered features
    sample_readings["DO_Temp_Ratio"] = sample_readings["DO"] / sample_readings["Temperature"]
    sample_readings["pH_Deviation"] = (sample_readings["pH"] - 7.0).abs()

    print(f"\n  Simulated Sibalom River field readings:")
    print(sample_readings[TRAINING_FEATURES].to_string(index=False))

    X_sample = scaler.transform(sample_readings[TRAINING_FEATURES])

    print("\n  Predictions:")
    for name, model in best_models.items():
        preds = le.inverse_transform(model.predict(X_sample))
        print(f"\n    {name}:")
        for i, (_, row) in enumerate(sample_readings.iterrows()):
            print(f"      Sample {i+1} (pH={row['pH']}, DO={row['DO']}, "
                  f"Temp={row['Temperature']}) -> {preds[i]}")


# =============================================================================
# 10. SAVE OUTPUTS
# =============================================================================
def save_processed_data(df):
    output_path = os.path.join(OUTPUT_DIR, "WQMA_JRS_with_WQI_classes.csv")
    df.to_csv(output_path, index=False)
    print(f"\n  -> Processed dataset saved: {output_path}")
    print(f"     Shape: {df.shape}")


# =============================================================================
# MAIN PIPELINE
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("  WATER QUALITY INDEX - ML PREDICTION PIPELINE")
    print("  JRS-WQMA 2020-2025 -> Sibalom River Transfer Learning")
    print("  Dataset: WQMA_JRS_2020_2025.csv (EMB Region 6)")
    print("=" * 70 + "\n")

    # 1. Load
    df = load_data(INPUT_CSV)

    # 2. Preprocess
    df = preprocess_data(df)

    # 3. Compute WQI
    df = compute_wqi_column(df)

    # 4. Feature Engineering
    weight_df = compute_feature_weights(df)

    # 5. WQI Classification
    df = create_classification_target(df)

    # 6. Correlation Heatmap
    plot_correlation_heatmap(df)

    # 7. Train & Evaluate Models
    results, best_models = train_and_evaluate(df)

    # 8. Comparison Summary
    summarize_results(results)

    # 9. Field Deployment Simulation
    simulate_field_prediction(best_models)

    # 10. Save Processed Data
    save_processed_data(df)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("  Models saved to: outputs/models/")
    print("  Plots  saved to: outputs/plots/")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
