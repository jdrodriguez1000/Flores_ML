import sqlite3
import uuid
import json
from datetime import datetime
from src.core.schemas import PredictionInput, PredictionOutput, FeedbackInput
from src.core.config import Settings

class AuditRepository:
    def __init__(self, db_path: str = None):
        settings = Settings()
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos y activa modo WAL."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    prediction_id TEXT PRIMARY KEY,
                    input_data TEXT,
                    output_data TEXT,
                    timestamp TEXT,
                    model_version TEXT,
                    shadow_mode INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    prediction_id TEXT PRIMARY KEY,
                    manual_species TEXT,
                    is_valid_sample INTEGER,
                    analyst_id TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (prediction_id) REFERENCES predictions (prediction_id)
                )
            """)

    def save_prediction(self, input_data: PredictionInput, output: PredictionOutput) -> str:
        """Persiste en SQLite y retorna UUID."""
        prediction_id = str(uuid.uuid4())
        output.prediction_id = prediction_id
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?)",
                (
                    prediction_id,
                    input_data.model_dump_json(),
                    output.model_dump_json(),
                    output.prediction_timestamp.isoformat(),
                    output.model_version,
                    1 if output.shadow_mode else 0
                )
            )
        return prediction_id

    def update_feedback(self, feedback: FeedbackInput) -> bool:
        """Actualiza el registro con la corrección del analista."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO feedback VALUES (?, ?, ?, ?, ?)",
                    (
                        feedback.prediction_id,
                        feedback.manual_species,
                        1 if feedback.is_valid_sample else 0,
                        feedback.analyst_id,
                        datetime.now().isoformat()
                    )
                )
            return True
        except sqlite3.Error:
            return False
