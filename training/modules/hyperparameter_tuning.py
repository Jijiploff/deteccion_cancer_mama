import time

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb


XGBOOST_GRID = {
    "n_estimators": [50, 100, 200],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.01, 0.1, 0.3],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
}

RF_GRID = {
    "n_estimators": [50, 100, 200],
    "max_depth": [4, 6, 8, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}


def run_grid_search(model_name, X, y, param_grid, n_folds=5, random_state=42):
    if model_name == "XGBoost":
        estimator = xgb.XGBClassifier(random_state=random_state, eval_metric="logloss")
    else:
        estimator = RandomForestClassifier(random_state=random_state)

    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    start = time.perf_counter()
    grid = GridSearchCV(
        estimator=estimator,
        param_grid=param_grid,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1,
        verbose=0,
    )
    grid.fit(X, y)
    elapsed = time.perf_counter() - start

    results_df = pd.DataFrame(grid.cv_results_)
    return {
        "model_name": model_name,
        "best_params": grid.best_params_,
        "best_score": float(grid.best_score_),
        "total_combinations": len(results_df),
        "total_time_s": round(elapsed, 3),
        "cv_results_df": results_df,
        "best_estimator": grid.best_estimator_,
    }


def plot_tuning_heatmap(grid_result, param_x, param_y, metric="mean_test_score") -> go.Figure:
    df = grid_result["cv_results_df"]
    if param_x not in df.columns or param_y not in df.columns:
        return None
    x_col = f"param_{param_x}"
    y_col = f"param_{param_y}"
    if x_col not in df.columns or y_col not in df.columns:
        return None

    pivot = df.pivot_table(index=y_col, columns=x_col, values=metric, aggfunc="mean")
    fig = px.imshow(
        pivot,
        text_auto=".3f",
        color_continuous_scale="Viridis",
        aspect="auto",
        height=400,
    )
    fig.update_layout(
        title=f"Heatmap: {param_x} vs {param_y} - {grid_result['model_name']}",
        xaxis_title=param_x,
        yaxis_title=param_y,
        margin=dict(t=40),
    )
    return fig


def format_best_params_table(grid_result) -> pd.DataFrame:
    rows = []
    best = grid_result["best_params"]
    df = grid_result["cv_results_df"]
    for param, best_val in best.items():
        param_col = f"param_{param}"
        if param_col in df.columns:
            evaluated = df[param_col].unique()
            rows.append({
                "Parámetro": param,
                "Valores Evaluados": ", ".join(str(v) for v in sorted(evaluated, key=str)),
                "Mejor Valor": str(best_val),
            })
    return pd.DataFrame(rows)
