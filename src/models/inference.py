import time
import random
import joblib
import numpy as np
from datetime import datetime
from src.core.schemas import PredictionInput, PredictionOutput, SpeciesEnum
from src.core.config import Settings

_SPECIES_MAP = {
    0: SpeciesEnum.SETOSA,
    1: SpeciesEnum.VERSICOLOR,
    2: SpeciesEnum.VIRGINICA
}

class InferenceEngine:
    def __init__(self, model_path: str):
        self.settings = Settings()
        self.model_version = "v1.0.0"
        self._model = None
        self.reload_model(model_path)

    def predict(self, data: PredictionInput) -> PredictionOutput:
        """Inferencia + Virginica Shield + Audit Randomizer."""
        start_time = time.time()
        
        if self._model is None:
            raise RuntimeError("Model is not loaded.")
            
        features = np.array([[
            data.sepal_length,
            data.sepal_width,
            data.petal_length,
            data.petal_width
        ]])
        
        # Inferencia
        probas = self._model.predict_proba(features)[0]
        class_idx = int(np.argmax(probas))
        confidence = float(probas[class_idx])
        species = _SPECIES_MAP[class_idx]
        
        # Lógica de "Shielding" y "Audit"
        needs_review = False
        
        # 1. General Shield
        if confidence < self.settings.CONFIDENCE_THRESHOLD:
            needs_review = True
            
        # 2. Virginica Shield
        if species == SpeciesEnum.VIRGINICA and confidence < self.settings.VIRGINICA_THRESHOLD:
            needs_review = True
            
        # 3. Audit Randomizer (5%)
        # Forzamos needs_review basado en una probabilidad aleatoria
        if random.random() < self.settings.AUDIT_RATE:
            needs_review = True
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return PredictionOutput(
            species=species,
            confidence=confidence,
            needs_review=needs_review,
            model_version=self.model_version,
            prediction_timestamp=datetime.now(),
            execution_time_ms=execution_time_ms,
            shadow_mode=self.settings.SHADOW_MODE,
            prediction_id=None
        )

    def reload_model(self, new_path: str) -> bool:
        """Hot-Swapping: Carga nuevo modelo sin reiniciar proceso."""
        try:
            self._model = joblib.load(new_path)
            return True
        except Exception:
            # En producción esto registraría el error en logs
            self._model = None
            return False

    def get_version(self) -> str:
        return self.model_version


class MockInferenceEngine(InferenceEngine):
    """Implementación Dummy para la Bala Trazadora (T-2.1.2)."""
    def __init__(self):
        self.settings = Settings()
        self.model_version = "v0.0.0-mock"
        self._model = None

    def predict(self, data: PredictionInput) -> PredictionOutput:
        return PredictionOutput(
            species=SpeciesEnum.SETOSA,
            confidence=1.0,
            needs_review=False,
            model_version=self.get_version(),
            prediction_timestamp=datetime.now(),
            execution_time_ms=5.0,
            shadow_mode=self.settings.SHADOW_MODE,
            prediction_id=None
        )
