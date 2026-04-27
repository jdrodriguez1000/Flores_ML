import pytest
import pandas as pd
import numpy as np

# En la fase RED, estos imports fallarán porque los módulos/clases no existen
from src.data.transformation import DataProcessor
from src.core.exceptions import RangeValidationError, NullInputError

@pytest.fixture
def processor():
    return DataProcessor()

def test_process_batch_rechazo_valores_fuera_de_rango(processor):
    """
    Escenario: Rechazo de valores fuera de rango biológico (Extremos y Negativos)
    CA: Valores < 0.1 o > 15.0 cm disparan RangeValidationError (ERR_01).
    """
    df_out_of_bounds = pd.DataFrame({
        "Id": [1, 2],
        "SepalLengthCm": [25.0, 5.1],  # 25.0 > 15.0
        "SepalWidthCm": [3.5, -1.0],   # -1.0 < 0.1
        "PetalLengthCm": [1.4, 1.4],
        "PetalWidthCm": [0.2, 0.2],
        "Species": ["Iris-setosa", "Iris-setosa"]
    })
    
    with pytest.raises(RangeValidationError) as exc_info:
        processor.process_batch(df_out_of_bounds)
    
    # Verificamos que contenga el código de error del contrato
    assert "ERR_01" in str(exc_info.value) or "RangeValidationError" in str(exc_info.value)


def test_process_batch_rechazo_por_nulos(processor):
    """
    Escenario: Rechazo por valores nulos (Hard Reject)
    CA: Presencia de null o NaN dispara NullInputError (ERR_04).
    """
    df_with_nulls = pd.DataFrame({
        "Id": [1, 2],
        "SepalLengthCm": [5.1, 4.9],
        "SepalWidthCm": [np.nan, 3.0], # NaN introduce nulo
        "PetalLengthCm": [1.4, 1.4],
        "PetalWidthCm": [0.2, 0.2],
        "Species": ["Iris-setosa", "Iris-setosa"]
    })
    
    with pytest.raises(NullInputError) as exc_info:
        processor.process_batch(df_with_nulls)
        
    assert "ERR_04" in str(exc_info.value) or "NullInputError" in str(exc_info.value)
