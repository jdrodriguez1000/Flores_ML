import pytest
import pandas as pd
import numpy as np
import warnings

# Fase RED: En este momento `StatisticalDriftWarning` y el método `check_drift`
# en `DataProcessor` no están implementados, lo que causará que el test falle.
from src.data.transformation import DataProcessor
from src.core.exceptions import StatisticalDriftWarning

def test_statistical_drift_detection():
    """
    Escenario: Detección de Deriva Distribucional (Drift Detection)
    CA: Si la media de un batch (n=100) se desvía > 3 sigma respecto al baseline,
    se debe disparar un StatisticalDriftWarning (ERR_06) sin bloquear la inferencia.
    (Según contrato: Z-score > 3).
    """
    processor = DataProcessor()
    
    # Estadísticas de entrenamiento (baseline)
    baseline_stats = {
        "sepal_length": {"mean": 5.0, "std": 1.0},
        "sepal_width": {"mean": 3.0, "std": 0.5},
        "petal_length": {"mean": 4.0, "std": 1.0},
        "petal_width": {"mean": 1.0, "std": 0.5}
    }
    
    # Creamos un batch de 100 registros.
    # Provocamos deriva en 'sepal_length' para que Z-score > 3.
    # Media baseline = 5.0, std = 1.0. Necesitamos media > 8.0.
    np.random.seed(42)
    drifted_data = {
        "sepal_length": np.random.normal(8.5, 0.5, 100),
        "sepal_width": np.random.normal(3.0, 0.5, 100),
        "petal_length": np.random.normal(4.0, 1.0, 100),
        "petal_width": np.random.normal(1.0, 0.5, 100),
        "species": ["Setosa"] * 100
    }
    df_batch = pd.DataFrame(drifted_data)
    
    # La validación de drift debe ser no bloqueante y disparar un warning.
    with pytest.warns(StatisticalDriftWarning) as record:
        processor.check_drift(df_batch, baseline_stats)
        
    # Verificar que el warning fue emitido
    assert len(record) >= 1
    
    # Validar el código de error y el tipo de warning en el mensaje
    warning_msg = str(record[0].message)
    assert "ERR_06" in warning_msg or "StatisticalDriftWarning" in warning_msg
