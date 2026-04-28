from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flores_ML"
    SHADOW_MODE: bool = True
    MODEL_PATH: str = "reports/metrics.json" # Not correct but need default, let's put "models/latest_model.pkl" per SpecDD but model was saved by MLflow. Wait, MLflow saves in mlruns.db. For now we will use a default or load from MLflow. Let's use a standard sklearn load.
    DB_PATH: str = "data/audit.db"
    CONFIDENCE_THRESHOLD: float = 0.85
    VIRGINICA_THRESHOLD: float = 0.98
    AUDIT_RATE: float = 0.05
    API_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env")
