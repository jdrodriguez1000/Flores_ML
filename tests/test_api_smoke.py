import pytest
import requests
import time
import subprocess
import os

def test_api_smoke_health():
    """T-2.1.3.SMK.RED: Test de salud de la API ejecutándose."""
    # Intentamos conectar a la API. Debería fallar si no está corriendo.
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("API no está en ejecución en localhost:8000 (RED)")
