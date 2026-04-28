import os
import mlflow

def test_mlflow_tracking_connection_successful():
    """
    T-2.1.2.MLO.GRN: Configuración de Tracking & Registro.
    Servidor activo (MLflow), test de conexión es GREEN.
    """
    # Restauramos variables de entorno por si acaso
    os.environ.pop("MLFLOW_HTTP_REQUEST_MAX_RETRIES", None)
    os.environ.pop("MLFLOW_HTTP_REQUEST_TIMEOUT", None)
        
    mlflow.set_tracking_uri("sqlite:///mlruns.db")
    
    # Esto debe funcionar sin lanzar excepciones porque el servidor estará arriba
    experiment = mlflow.set_experiment("dummy_experiment")
    assert experiment is not None
    assert experiment.name == "dummy_experiment"
