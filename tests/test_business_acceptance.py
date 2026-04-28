import json
import pytest
import os

METRICS_FILE = "reports/metrics.json"

def test_business_acceptance_thresholds():
    """
    Test de Umbral de Aceptación de Negocio (BRD).
    Valida que el modelo entrenado cumpla con los KPIs requeridos:
    - Global Accuracy > 96%
    - F1-Score (Especie Virginica) > 98%
    """
    assert os.path.exists(METRICS_FILE), f"No se encontró el reporte de métricas en {METRICS_FILE}. El modelo debe ser entrenado primero."

    with open(METRICS_FILE, "r") as f:
        metrics = json.load(f)

    # Umbrales definidos en el BRD
    min_accuracy = 0.96
    min_f1_virginica = 0.98

    # Extracción de métricas
    accuracy = metrics.get("accuracy")
    f1_virginica = metrics.get("f1_score_virginica")

    assert accuracy is not None, "El reporte de métricas debe contener 'accuracy'"
    assert f1_virginica is not None, "El reporte de métricas debe contener 'f1_score_virginica'"

    # Validación de umbrales
    assert accuracy > min_accuracy, f"El Accuracy Global ({accuracy:.4f}) no supera el umbral de negocio ({min_accuracy})"
    assert f1_virginica > min_f1_virginica, f"El F1-Score de Virginica ({f1_virginica:.4f}) no supera el umbral de negocio ({min_f1_virginica})"
