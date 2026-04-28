import pytest
import json
import io
from contextlib import redirect_stdout
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_structured_logging():
    """T-2.1.3.OBS.RED: Verifica que la API emita logs estructurados en JSON."""
    f = io.StringIO()
    with redirect_stdout(f):
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        
    output = f.getvalue()
    print(f"\nCaptured stdout: {output}")
    
    # Buscamos una línea que sea un JSON válido (debería fallar si no hay logs JSON)
    json_logs = []
    for line in output.splitlines():
        try:
            log_data = json.loads(line)
            json_logs.append(log_data)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) > 0, "No se encontraron logs estructurados en JSON en stdout."
    
    # Verificamos campos mínimos de observabilidad
    log = json_logs[0]
    assert "event" in log or "message" in log
    assert "timestamp" in log
