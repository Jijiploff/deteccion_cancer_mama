import time
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report,
)
import xgboost as xgb
import joblib


def prepare_wisconsin_data(wisconsin_data: pd.DataFrame, test_size=0.2, random_state=42):
    df = wisconsin_data.drop(["id", "Unnamed: 32"], axis=1, errors="ignore").dropna()
    X = df.drop("diagnosis", axis=1)
    y = (df["diagnosis"] == "M").astype(int)
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def train_xgboost(X_train, y_train, X_test=None, y_test=None, params=None):
    if params is None:
        params = {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "eval_metric": "logloss",
        }
    model = xgb.XGBClassifier(**params)
    start = time.perf_counter()
    eval_set = [(X_test, y_test)] if X_test is not None and y_test is not None else None
    model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
    elapsed = time.perf_counter() - start
    return model, elapsed


def train_random_forest(X_train, y_train, params=None):
    if params is None:
        params = {
            "n_estimators": 100,
            "max_depth": 6,
            "min_samples_split": 2,
            "random_state": 42,
        }
    model = RandomForestClassifier(**params)
    start = time.perf_counter()
    model.fit(X_train, y_train)
    elapsed = time.perf_counter() - start
    return model, elapsed


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "auc": roc_auc_score(y_test, y_proba),
        "y_pred": y_pred,
        "y_proba": y_proba,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }


def plot_confusion_matrix(cm: dict, title="Matriz de Confusión") -> go.Figure:
    matrix = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
    labels = [["BENIGN (VP)", "MALIGNANT (FP)"], ["BENIGN (FN)", "MALIGNANT (VP)"]]
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=["Pred: BENIGN", "Pred: MALIGNANT"],
        y=["Real: BENIGN", "Real: MALIGNANT"],
        text=[[f"{v}<br><sub>{l}</sub>" for v, l in zip(row, lab)] for row, lab in zip(matrix, labels)],
        texttemplate="%{text}",
        colorscale="Blues",
        showscale=False,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Predicción",
        yaxis_title="Real",
        height=400,
        margin=dict(t=40),
    )
    return fig


def plot_roc_curve(y_test, probas_dict: dict) -> go.Figure:
    fig = go.Figure()
    colors = {"XGBoost": "#8B5CF6", "Random Forest": "#22c55e"}
    for name, y_proba in probas_dict.items():
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr, mode="lines",
            name=f"{name} (AUC = {auc:.3f})",
            line=dict(color=colors.get(name, "#3b82f6"), width=2),
        ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="Aleatorio (AUC = 0.5)",
        line=dict(color="gray", dash="dash"),
    ))
    fig.update_layout(
        title="Curvas ROC - Comparación de Modelos",
        xaxis_title="Tasa de Falsos Positivos (1 - Especificidad)",
        yaxis_title="Tasa de Verdaderos Positivos (Sensibilidad)",
        height=500,
        margin=dict(t=40),
        legend=dict(x=0.6, y=0.1),
    )
    return fig


def plot_feature_importance(model, feature_names, title="Importancia de Características", n_top=15) -> go.Figure:
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        return None
    df = pd.DataFrame({"Característica": feature_names, "Importancia": importances})
    df = df.sort_values("Importancia", ascending=True).tail(n_top)
    fig = px.bar(
        df, x="Importancia", y="Característica",
        orientation="h", title=title,
        color="Importancia", color_continuous_scale="purples",
    )
    fig.update_layout(height=400 + n_top * 10, margin=dict(t=40))
    return fig


def plot_metrics_comparison(results: dict) -> go.Figure:
    metrics = ["accuracy", "precision", "recall", "f1", "auc"]
    fig = go.Figure()
    colors = {"XGBoost": "#8B5CF6", "Random Forest": "#22c55e"}
    for name, res in results.items():
        vals = [res["accuracy"], res["precision"], res["recall"], res["f1"], res["auc"]]
        fig.add_trace(go.Bar(
            name=name, x=metrics, y=vals,
            marker_color=colors.get(name, "#3b82f6"),
            text=[f"{v:.3f}" for v in vals],
            textposition="outside",
        ))
    fig.update_layout(
        title="Comparación de Métricas entre Modelos",
        yaxis_title="Valor",
        yaxis_range=[0, 1],
        height=400,
        margin=dict(t=40),
        barmode="group",
    )
    return fig


def save_model(model, model_name: str, results_dir: Path, models_dir: Path, metrics: dict, params: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name}_{timestamp}.pkl"
    model_path = models_dir / filename
    joblib.dump(model, model_path)

    metadata = {
        "model_name": model_name,
        "filename": filename,
        "timestamp": timestamp,
        "metrics": {k: v for k, v in metrics.items() if isinstance(v, (int, float, str))},
        "params": {k: str(v) if isinstance(v, Path) else v for k, v in params.items()},
    }
    meta_path = results_dir / f"{model_name}_metadata_{timestamp}.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return model_path, meta_path
