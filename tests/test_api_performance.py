import pytest
import time
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_latency_p95():
    """T-2.1.3.PERF.RED: Verifica que la latencia de la API sea < 3s."""
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    
    latencies = []
    for _ in range(10):  # Realizamos 10 peticiones para medir
        start_time = time.time()
        response = client.post("/api/v1/predict", json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        latencies.append(end_time - start_time)
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f"\nLatency - Avg: {avg_latency:.4f}s, Max: {max_latency:.4f}s")
    
    # El requerimiento es < 3s (behavior.md)
    assert max_latency < 3.0
