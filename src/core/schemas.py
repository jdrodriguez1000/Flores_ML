from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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
