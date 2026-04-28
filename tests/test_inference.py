import pytest
from datetime import datetime
from src.core.schemas import PredictionInput, SpeciesEnum

def test_inference_engine_predict():
    # Attempt to import InferenceEngine, should fail if it doesn't exist
    from src.models.inference import InferenceEngine

    engine = InferenceEngine(model_path="models/latest_model.pkl")
    
    input_data = PredictionInput(
        sepal_length=5.1,
        sepal_width=3.5,
        petal_length=1.4,
        petal_width=0.2
    )

    output = engine.predict(input_data)
    
    assert output is not None
    assert output.species in [SpeciesEnum.SETOSA, SpeciesEnum.VERSICOLOR, SpeciesEnum.VIRGINICA]
    assert 0.0 <= output.confidence <= 1.0
    assert isinstance(output.needs_review, bool)
    assert isinstance(output.model_version, str)
    assert isinstance(output.prediction_timestamp, datetime)
    assert isinstance(output.execution_time_ms, float)
    assert isinstance(output.shadow_mode, bool)
