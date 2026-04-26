# Specification-Driven Development (SpecDD) - Flores_ML

## 1. Introducción
Este documento es la **Fuente de Verdad Única**. Define los contratos para el Core y los Adaptadores. Prioriza el desacoplamiento y la seguridad biológica (Virginica Shield).

---

## 2. Configuración Centralizada (src/core/config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flores_ML"
    SHADOW_MODE: bool = True
    MODEL_PATH: str = "models/latest_model.pkl"
    DB_PATH: str = "data/audit.db"
    CONFIDENCE_THRESHOLD: float = 0.85
    VIRGINICA_THRESHOLD: float = 0.98
    AUDIT_RATE: float = 0.05
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
```

---

## 3. Esquemas de Datos y Tipado Estricto (src/core/schemas.py)

```python
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SpeciesEnum(str, Enum):
    SETOSA = "Setosa"
    VERSICOLOR = "Versicolor"
    VIRGINICA = "Virginica"

class PredictionInput(BaseModel):
    sepal_length: float = Field(..., ge=0.1, le=15.0)
    sepal_width: float = Field(..., ge=0.1, le=15.0)
    petal_length: float = Field(..., ge=0.1, le=15.0)
    petal_width: float = Field(..., ge=0.1, le=15.0)

class PredictionOutput(BaseModel):
    species: SpeciesEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_review: bool
    model_version: str
    prediction_timestamp: datetime
    execution_time_ms: float
    shadow_mode: bool
    prediction_id: Optional[str] = None

class FeedbackInput(BaseModel):
    prediction_id: str
    manual_species: SpeciesEnum
    is_valid_sample: bool
    analyst_id: str
```

---

## 4. Orquestador de Negocio (src/core/service.py)
```python
class PredictionService:
    def __init__(self, processor: "DataProcessor", engine: "InferenceEngine", repo: "AuditRepository"):
        self.processor = processor
        self.engine = engine
        self.repo = repo

    def predict_and_audit(self, data: PredictionInput) -> PredictionOutput:
        """
        Flujo de Inferencia Web: 
        Process (Single) -> Predict -> Save Audit -> Return.
        """
        pass
```

---

## 5. Repositorio de Auditoría (src/core/repository.py)
```python
class AuditRepository:
    def save_prediction(self, input_data: PredictionInput, output: PredictionOutput) -> str:
        """Persiste en SQLite (WAL Mode) y retorna UUID."""
        pass

    def update_feedback(self, feedback: FeedbackInput) -> bool:
        """Actualiza el registro con la corrección del analista."""
        pass
```

---

## 6. Motor de Inferencia (src/model/inference.py)
```python
class InferenceEngine:
    def __init__(self, model_path: str):
        self.model_version = "v1.0.0"

    def predict(self, data: PredictionInput) -> PredictionOutput:
        """Inferencia + Virginica Shield + Audit Randomizer."""
        pass

    def reload_model(self, new_path: str) -> bool:
        """Hot-Swapping: Carga nuevo modelo sin reiniciar proceso."""
        pass

    def get_version(self) -> str:
        return self.model_version

class MockInferenceEngine(InferenceEngine):
    """Implementación Dummy para la Bala Trazadora (T-2.1.2)."""
    def __init__(self):
        super().__init__("mock_path")
        self.model_version = "v0.0.0-mock"

    def predict(self, data: PredictionInput) -> PredictionOutput:
        return PredictionOutput(
            species=SpeciesEnum.SETOSA, 
            confidence=1.0,
            needs_review=False,
            model_version=self.get_version(),
            prediction_timestamp=datetime.now(),
            execution_time_ms=5.0,
            shadow_mode=True
        )
```

---

## 7. Capa de Datos (src/data/transformation.py)
**Módulo Profundo:** Maneja tanto registros individuales como procesamiento por lotes.

```python
import pandas as pd

class DataProcessor:
    def process_input(self, data: PredictionInput) -> PredictionInput:
        """Validación de un solo registro (API)."""
        pass

    def process_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implementa el Leakage Shield para el pipeline de Ingesta (T-2.1.1):
        1. Drop 'Id'.
        2. Validación de rangos en todo el set.
        3. Normalización de nombres de columnas.
        """
        pass
```

---

## 8. Adaptadores: API y UI (src/api/ & src/ui/)
- `POST /api/v1/predict`: Entrada `PredictionInput`, salida `PredictionOutput`.
- `POST /api/v1/feedback`: Entrada `FeedbackInput`.
- `GET /api/v1/health`: Estado del sistema y versión del modelo.

---

## 9. Definición de la Bala Trazadora (Iteración 2.1)
El **Tracer Bullet** se compone de dos flujos separados:
1. **Flujo de Ingesta (T-2.1.1):** `CSV -> DataProcessor.process_batch -> DataFrame Silver` (Valida Leakage Shield).
2. **Flujo de Inferencia (T-2.1.3):** `UI -> API -> PredictionService (con MockInferenceEngine) -> UI` (Valida Arquitectura Web y Auditoría).

---

## 10. Matriz de Errores Técnicos (Para TDD y API)

La API debe interceptar estas excepciones y devolver un **HTTP 400/500** con el siguiente esquema JSON unificado:
```json
{
  "error_code": "ERR_XX",
  "message": "Mensaje legible",
  "detail": [{"loc": ["campo"], "msg": "detalle técnico"}]
}
```

| Excepción | Código | Descripción | HTTP Status |
| :--- | :--- | :--- | :--- |
| `RangeValidationError` | ERR_01 | Valores fuera de 0.1 - 15.0 cm. | 400 |
| `ModelLoadError` | ERR_02 | Fallo al cargar el archivo .pkl. | 503 |
| `AuditStorageError` | ERR_03 | Fallo al escribir en SQLite. | 500 |
| `NullInputError` | ERR_04 | Intento de enviar campos vacíos. | 400 |
| `LogicConsistencyError` | ERR_05 | Inconsistencia biológica (ej: ancho > largo). | 400 |
| `StatisticalDriftWarning` | ERR_06 | Alerta de deriva estadística (Non-Blocking). | 200 |
| `SchemaValidationError` | ERR_07 | Error de tipado estricto (ej: string en vez de float) o Enum inválido. | 422 |
