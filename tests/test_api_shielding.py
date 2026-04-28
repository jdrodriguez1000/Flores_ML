import pytest
from fastapi.testclient import TestClient
from src.core.config import Settings
from src.core.schemas import SpeciesEnum

# Intentamos importar la app, fallará porque aún no existe (RED)
try:
    from src.api.main import app
    client = TestClient(app)
except ImportError:
    app = None
    client = None

@pytest.fixture
def settings():
    return Settings()

def test_api_shadow_mode_status():
    """T-2.1.3.SHW.RED: Verifica que la API reporte shadow_mode=True cuando está activo."""
    if client is None:
        pytest.fail("API main.app no implementada (RED)")
        
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/api/v1/predict", json=payload)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["shadow_mode"] is True

def test_api_virginica_shield_trigger():
    """T-2.1.3.RED: Verifica el 'Virginica Shield' (confianza < 98% -> needs_review=True)."""
    if client is None:
        pytest.fail("API main.app no implementada (RED)")
        
    # Medidas que forzarían una Virginica con baja confianza (frontera)
    # Según behavior.md: 6.0, 2.7, 5.1, 1.8
    payload = {
        "sepal_length": 6.0,
        "sepal_width": 2.7,
        "petal_length": 5.1,
        "petal_width": 1.8
    }
    response = client.post("/api/v1/predict", json=payload)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    
    # Si es Virginica y la confianza es baja, debe pedir revisión
    if data["species"] == SpeciesEnum.VIRGINICA:
        if data["confidence"] < 0.98:
            assert data["needs_review"] is True

def test_api_low_confidence_shield():
    """T-2.1.3.RED: Verifica el escudo general de baja confianza (< 85%)."""
    if client is None:
        pytest.fail("API main.app no implementada (RED)")
        
    # Medidas de ambigüedad general (behavior.md: 6.0, 2.5, 4.8, 1.6)
    payload = {
        "sepal_length": 6.0,
        "sepal_width": 2.5,
        "petal_length": 4.8,
        "petal_width": 1.6
    }
    response = client.post("/api/v1/predict", json=payload)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    
    if data["confidence"] < 0.85:
        assert data["needs_review"] is True

def test_api_health_endpoint():
    """Verifica el endpoint de salud (SpecDD)."""
    if client is None:
        pytest.fail("API main.app no implementada (RED)")
        
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "model_version" in response.json()
