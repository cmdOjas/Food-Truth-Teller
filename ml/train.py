"""
ML Training Pipeline: Decision Tree vs Random Forest
Generates accuracy, precision, recall, F1, confusion matrix, and ROC curve.
Saves the best model to models/health_model.pkl.

Usage:
    python train.py
    python train.py --dataset dataset/food_health_dataset.csv
"""
from __future__ import annotations
import argparse
import os
import sys
import json

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    auc,
    classification_report,
)
from sklearn.pipeline import Pipeline

from nlp_processor import NLPProcessor

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def load_data(csv_path: str) -> tuple[list[str], list[int]]:
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["ingredients", "label"])
    processor = NLPProcessor()
    X = [processor.process(text) for text in df["ingredients"].tolist()]
    y = df["label"].astype(int).tolist()
    return X, y


def evaluate_model(name: str, model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
        "precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
    }

    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  Accuracy : {metrics['accuracy']}%")
    print(f"  Precision: {metrics['precision']}%")
    print(f"  Recall   : {metrics['recall']}%")
    print(f"  F1 Score : {metrics['f1_score']}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Safe", "Avoid"]))

    _plot_confusion_matrix(name, confusion_matrix(y_test, y_pred))
    _plot_roc(name, y_test, y_proba)

    return metrics


def _plot_confusion_matrix(name: str, cm: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Safe", "Avoid"], yticklabels=["Safe", "Avoid"], ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {name}")
    plt.tight_layout()
    safe_name = name.replace(" ", "_").lower()
    fig.savefig(os.path.join(PLOTS_DIR, f"confusion_matrix_{safe_name}.png"), dpi=120)
    plt.close(fig)


def _plot_roc(name: str, y_test, y_proba) -> None:
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="darkorange", lw=2, label=f"AUC = {roc_auc:.3f}")
    ax.plot([0, 1], [0, 1], color="navy", lw=1, linestyle="--")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Curve — {name}")
    ax.legend(loc="lower right")
    plt.tight_layout()
    safe_name = name.replace(" ", "_").lower()
    fig.savefig(os.path.join(PLOTS_DIR, f"roc_curve_{safe_name}.png"), dpi=120)
    plt.close(fig)


def train(csv_path: str) -> None:
    print(f"Loading dataset from: {csv_path}")
    X, y = load_data(csv_path)
    print(f"Samples: {len(X)} | Class distribution: Safe={y.count(0)}, Avoid={y.count(1)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        min_df=1,
        sublinear_tf=True,
    )

    dt_pipeline = Pipeline([
        ("tfidf", vectorizer),
        ("clf", DecisionTreeClassifier(max_depth=15, min_samples_split=4, random_state=42)),
    ])

    rf_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1, sublinear_tf=True)),
        ("clf", RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=3, random_state=42, n_jobs=-1)),
    ])

    print("\nTraining Decision Tree...")
    dt_pipeline.fit(X_train, y_train)

    print("Training Random Forest...")
    rf_pipeline.fit(X_train, y_train)

    dt_metrics = evaluate_model("Decision Tree", dt_pipeline, X_test, y_test)
    rf_metrics = evaluate_model("Random Forest", rf_pipeline, X_test, y_test)

    # Cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    dt_cv = cross_val_score(dt_pipeline, X, y, cv=skf, scoring="f1")
    rf_cv = cross_val_score(rf_pipeline, X, y, cv=skf, scoring="f1")
    print(f"\nCross-validation F1 — Decision Tree: {dt_cv.mean():.3f} ± {dt_cv.std():.3f}")
    print(f"Cross-validation F1 — Random Forest: {rf_cv.mean():.3f} ± {rf_cv.std():.3f}")

    best_pipeline = rf_pipeline if rf_metrics["f1_score"] >= dt_metrics["f1_score"] else dt_pipeline
    best_name = "Random Forest" if rf_metrics["f1_score"] >= dt_metrics["f1_score"] else "Decision Tree"
    print(f"\nBest model: {best_name} (F1={max(rf_metrics['f1_score'], dt_metrics['f1_score'])}%)")

    model_path = os.path.join(MODELS_DIR, "health_model.pkl")
    vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")

    # Save entire pipeline (vectorizer + classifier)
    joblib.dump(best_pipeline, model_path)
    joblib.dump(best_pipeline.named_steps["tfidf"], vectorizer_path)
    print(f"\nModel saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")

    report = {
        "best_model": best_name,
        "decision_tree": dt_metrics,
        "random_forest": rf_metrics,
        "cross_validation": {
            "decision_tree_f1_mean": round(float(dt_cv.mean()), 4),
            "decision_tree_f1_std": round(float(dt_cv.std()), 4),
            "random_forest_f1_mean": round(float(rf_cv.mean()), 4),
            "random_forest_f1_std": round(float(rf_cv.std()), 4),
        },
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    report_path = os.path.join(MODELS_DIR, "training_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Training report saved to: {report_path}")
    print(f"Plots saved to: {PLOTS_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the food health classifier")
    parser.add_argument("--dataset", default=os.path.join(os.path.dirname(__file__), "dataset", "food_health_dataset.csv"))
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset not found at {args.dataset}. Generating it first...")
        os.system(f"python {os.path.join(os.path.dirname(__file__), 'dataset', 'generate_dataset.py')}")

    train(args.dataset)
