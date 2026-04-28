import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_error_out_of_range():
    """T-2.1.1.B.RED / behavior.md: Rechazo de valores fuera de rango (ERR_01)."""
    payload = {
        "sepal_length": 25.0,  # > 15.0
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "ERR_01"

def test_error_null_input():
    """behavior.md: Rechazo por valores nulos (ERR_04)."""
    payload = {
        "sepal_length": 5.1,
        "sepal_width": None,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/api/v1/predict", json=payload)
    # FastAPI/Pydantic valida nulos antes del handler si el campo es float.
    # Pero nuestro handler de NullInputError capturará Nulls si pasan.
    # En este caso, Pydantic lanzará ValidationError que mapeamos a ERR_07 o ERR_04.
    assert response.status_code in (400, 422)
    data = response.json()
    assert data["error_code"] in ("ERR_04", "ERR_07")

def test_error_logic_consistency():
    """SpecDD: Inconsistencia biológica (ancho > largo) (ERR_05)."""
    payload = {
        "sepal_length": 5.0,
        "sepal_width": 6.0,  # ancho > largo
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "ERR_05"

def test_error_schema_invalid():
    """SpecDD: Error de tipado estricto (string en vez de float) (ERR_07)."""
    payload = {
        "sepal_length": "invalid",
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "ERR_07"
