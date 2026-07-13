import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import chi2_contingency, wilcoxon
from sklearn.metrics import confusion_matrix


def mcnemar_test(y_true, y_pred_model1, y_pred_model2):
    """
    Prueba de McNemar para comparar dos modelos.
    H0: No hay diferencia en las proporciones de error entre modelos.
    """
    cm = confusion_matrix(
        (y_pred_model1 != y_true).astype(int),
        (y_pred_model2 != y_true).astype(int),
    )
    if cm.shape != (2, 2):
        return {"statistic": None, "p_value": None, "error": "Matriz no 2x2"}

    b = int(cm[0, 1])
    c = int(cm[1, 0])

    if b + c == 0:
        return {"statistic": 0.0, "p_value": 1.0, "note": "Modelos idénticos"}

    statistic = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = 1 - chi2_contingency([[0, b], [c, 0]], correction=False)[1]
    p_value = 1.0 - (1.0 - chi2_contingency([[b, 0], [0, c]], correction=False)[1])

    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(statistic, 1)

    return {"statistic": round(float(statistic), 4), "p_value": round(float(p_value), 4)}


def wilcoxon_test(y_true, y_proba_model1, y_proba_model2):
    """
    Prueba de Wilcoxon Signed-Rank para comparar probabilidades de dos modelos.
    H0: Las distribuciones de probabilidades son iguales.
    """
    diff = y_proba_model1 - y_proba_model2
    diff = diff[diff != 0]
    if len(diff) < 2:
        return {"statistic": None, "p_value": None, "note": "Diferencias insuficientes"}

    try:
        stat, p = wilcoxon(diff, alternative="two-sided")
        return {"statistic": round(float(stat), 4), "p_value": round(float(p_value), 4)}
    except ValueError as e:
        return {"statistic": None, "p_value": None, "error": str(e)}


def interpret_mcnemar(p_value, alpha=0.05):
    if p_value is None:
        return "No se pudo calcular."
    if p_value < alpha:
        return f"**Diferencias significativas** (p = {p_value:.4f} < {alpha}): Los modelos tienen rendimiento diferente."
    return f"**Sin diferencias significativas** (p = {p_value:.4f} ≥ {alpha}): Los modelos tienen rendimiento similar."


def interpret_wilcoxon(p_value, alpha=0.05):
    if p_value is None:
        return "No se pudo calcular."
    if p_value < alpha:
        return f"**Diferencias significativas** (p = {p_value:.4f} < {alpha}): Las distribuciones de probabilidad difieren."
    return f"**Sin diferencias significativas** (p = {p_value:.4f} ≥ {alpha}): Las distribuciones de probabilidad son similares."


def run_all_tests(models_data: dict, y_true) -> pd.DataFrame:
    """
    models_data: {name: {"y_pred": ..., "y_proba": ...}}
    y_true: valores reales
    """
    model_names = list(models_data.keys())
    rows = []

    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            n1, n2 = model_names[i], model_names[j]
            m1 = models_data[n1]
            m2 = models_data[n2]

            mcnemar = mcnemar_test(y_true, m1["y_pred"], m2["y_pred"])
            wilc = wilcoxon_test(y_true, m1["y_proba"], m2["y_proba"])

            rows.append({
                "Modelo A": n1,
                "Modelo B": n2,
                "McNemar χ²": mcnemar.get("statistic", "-"),
                "McNemar p-valor": mcnemar.get("p_value", "-"),
                "McNemar Interpretación": interpret_mcnemar(mcnemar.get("p_value")),
                "Wilcoxon W": wilc.get("statistic", "-"),
                "Wilcoxon p-valor": wilc.get("p_value", "-"),
                "Wilcoxon Interpretación": interpret_wilcoxon(wilc.get("p_value")),
            })

    return pd.DataFrame(rows)


def plot_pvalue_heatmap(test_results: pd.DataFrame) -> go.Figure:
    models = sorted(set(test_results["Modelo A"].tolist() + test_results["Modelo B"].tolist()))
    n = len(models)
    p_matrix = np.ones((n, n))

    for _, row in test_results.iterrows():
        i = models.index(row["Modelo A"])
        j = models.index(row["Modelo B"])
        try:
            p = float(row["McNemar p-valor"])
            p_matrix[i, j] = p
            p_matrix[j, i] = p
        except (ValueError, TypeError):
            pass

    fig = go.Figure(data=go.Heatmap(
        z=p_matrix,
        x=models,
        y=models,
        text=[[f"{v:.4f}" if v < 1 else "1.0" for v in row] for row in p_matrix],
        texttemplate="%{text}",
        colorscale="RdYlGn_r",
        zmin=0, zmax=1,
    ))
    fig.update_layout(
        title="Mapa de Calor - p-valores McNemar entre Modelos",
        height=400,
        margin=dict(t=40),
    )
    return fig
