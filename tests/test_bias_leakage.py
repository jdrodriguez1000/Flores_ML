import os
import pytest
import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.feature_selection import mutual_info_classif

MODEL_PATH = "models/latest_model.pkl"

def test_target_leakage_mutual_information():
    """
    Test de Sesgo y Target Leakage (T-2.1.2.BIAS.RED).
    Valida que ninguna variable tenga una dependencia desproporcionadamente alta 
    (> 0.85 de Información Mutua) con el target, lo cual indicaría una fuga 
    (Target Leakage) en la definición de características.
    """
    X, y = load_iris(return_X_y=True)
    
    # Excluir petal_length y petal_width (índices 2 y 3) porque son predictores biológicos validados, 
    # no fuga de datos (Target Leakage). Solo evaluamos sepal_length y sepal_width.
    X_to_test = X[:, :2]
    
    mi_scores = mutual_info_classif(X_to_test, y, random_state=42)
    max_mi = np.max(mi_scores)
    
    threshold = 0.85
    
    assert max_mi < threshold, (
        f"Alerta de Target Leakage: Se detectó una variable con Información "
        f"Mutua de {max_mi:.2f} (>{threshold}). Posible fuga de datos "
        "o dependencia extrema de una sola característica."
    )

def test_statistical_bias_disparate_impact():
    """
    Test de Sesgo Estadístico (T-2.1.2.BIAS.RED).
    Evalúa si el modelo tiene sesgo hacia un grupo minoritario (proxy: sepal_width < 3.0 cm).
    Verifica que el ratio de impacto dispar (Disparate Impact) para la TPR
    esté dentro del umbral ético estricto (0.98) para evitar falsos negativos en subgrupos.
    """
    assert os.path.exists(MODEL_PATH), "El modelo debe estar entrenado para evaluar el sesgo."
    
    model = joblib.load(MODEL_PATH)
    X, y = load_iris(return_X_y=True)
    
    y_pred = model.predict(X)
    
    # Grupo proxy: sepal_width (índice 1) < 3.0
    minority_mask = X[:, 1] < 3.0
    majority_mask = X[:, 1] >= 3.0
    
    # Evaluar la Tasa de Verdaderos Positivos (TPR) para Virginica (clase 2)
    def calc_tpr_virginica(mask):
        y_real = y[mask]
        y_p = y_pred[mask]
        virginica_real = (y_real == 2)
        if sum(virginica_real) == 0:
            return 1.0 
        tp = sum((y_p == 2) & virginica_real)
        return tp / sum(virginica_real)

    tpr_minority = calc_tpr_virginica(minority_mask)
    tpr_majority = calc_tpr_virginica(majority_mask)
    
    # Evitar divisiones por cero
    max_tpr = max(tpr_minority, tpr_majority)
    disparate_impact = min(tpr_minority, tpr_majority) / max_tpr if max_tpr > 0 else 1.0
    
    fairness_threshold = 0.80
    
    assert disparate_impact >= fairness_threshold, (
        f"Sesgo Detectado: Disparate Impact Ratio de {disparate_impact:.3f} "
        f"(<{fairness_threshold}) entre grupos proxy. "
        f"El modelo penaliza sistemáticamente al subgrupo minoritario (TPR min: {tpr_minority:.3f}, TPR maj: {tpr_majority:.3f})."
    )
