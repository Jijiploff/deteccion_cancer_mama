import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score

from modules.models import train_xgboost, train_random_forest, evaluate_model


def run_cross_validation(X, y, model_name, n_splits=5, params=None, random_state=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_results = []
    models = []
    start = time.perf_counter()

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
        X_train_f, X_test_f = X.iloc[train_idx], X.iloc[test_idx]
        y_train_f, y_test_f = y.iloc[train_idx], y.iloc[test_idx]

        if model_name == "XGBoost":
            model, _ = train_xgboost(X_train_f, y_train_f, X_test_f, y_test_f, params)
        else:
            model, _ = train_random_forest(X_train_f, y_train_f, params)

        y_pred = model.predict(X_test_f)
        y_proba = model.predict_proba(X_test_f)[:, 1]

        fold_results.append({
            "fold": fold,
            "accuracy": accuracy_score(y_test_f, y_pred),
            "auc": roc_auc_score(y_test_f, y_proba),
        })
        models.append(model)

    elapsed = time.perf_counter() - start
    accs = [r["accuracy"] for r in fold_results]
    aucs = [r["auc"] for r in fold_results]

    return {
        "model_name": model_name,
        "n_splits": n_splits,
        "fold_results": fold_results,
        "mean_accuracy": float(np.mean(accs)),
        "std_accuracy": float(np.std(accs)),
        "mean_auc": float(np.mean(aucs)),
        "std_auc": float(np.std(aucs)),
        "min_accuracy": float(np.min(accs)),
        "max_accuracy": float(np.max(accs)),
        "total_time_s": round(elapsed, 3),
        "models": models,
    }


def plot_cv_results(cv_results: dict) -> go.Figure:
    df = pd.DataFrame(cv_results["fold_results"])
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Accuracy",
        x=df["fold"].astype(str),
        y=df["accuracy"],
        text=df["accuracy"].round(4),
        textposition="outside",
        marker_color="#8B5CF6",
    ))
    fig.add_trace(go.Bar(
        name="AUC",
        x=df["fold"].astype(str),
        y=df["auc"],
        text=df["auc"].round(4),
        textposition="outside",
        marker_color="#22c55e",
    ))

    fig.update_layout(
        title=f"Validación Cruzada ({cv_results['n_splits']}-Fold) - {cv_results['model_name']}",
        xaxis_title="Fold",
        yaxis_title="Valor",
        yaxis_range=[0, 1],
        height=400,
        margin=dict(t=40),
        barmode="group",
    )
    return fig


def plot_cv_boxplot(all_cv: list[dict]) -> go.Figure:
    fig = go.Figure()
    for cv in all_cv:
        accs = [r["accuracy"] for r in cv["fold_results"]]
        fig.add_trace(go.Box(
            y=accs, name=cv["model_name"],
            boxmean=True,
        ))
    fig.update_layout(
        title="Distribución de Accuracy por Modelo (CV)",
        yaxis_title="Accuracy",
        yaxis_range=[0, 1],
        height=400,
        margin=dict(t=40),
    )
    return fig


def format_cv_table(cv_results: dict) -> pd.DataFrame:
    rows = []
    for r in cv_results["fold_results"]:
        rows.append({
            "Fold": f"Fold {r['fold']}",
            "Accuracy": f"{r['accuracy']:.4f}",
            "AUC": f"{r['auc']:.4f}",
        })
    rows.append({
        "Fold": "**Media**",
        "Accuracy": f"**{cv_results['mean_accuracy']:.4f}**",
        "AUC": f"**{cv_results['mean_auc']:.4f}**",
    })
    rows.append({
        "Fold": "Desv. Est.",
        "Accuracy": f"{cv_results['std_accuracy']:.4f}",
        "AUC": f"{cv_results['std_auc']:.4f}",
    })
    return pd.DataFrame(rows)
