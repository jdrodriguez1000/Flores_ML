from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flores_ML"
    SHADOW_MODE: bool = True
    MODEL_PATH: str = "models/latest_model.pkl"
    DB_PATH: str = "data/audit.db"
    CONFIDENCE_THRESHOLD: float = 0.85
    VIRGINICA_THRESHOLD: float = 0.98
    AUDIT_RATE: float = 0.05
    API_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env")
