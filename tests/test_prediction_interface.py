import pytest
from datetime import datetime
from pydantic import ValidationError

def test_prediction_output_schema():
    # Attempt to import the schema, should fail if it doesn't exist yet
    from src.core.schemas import PredictionOutput, SpeciesEnum
    
    # Valid output should pass validation
    valid_data = {
        "species": SpeciesEnum.SETOSA,
        "confidence": 0.95,
        "needs_review": False,
        "model_version": "v1.0.0",
        "prediction_timestamp": datetime.now(),
        "execution_time_ms": 15.5,
        "shadow_mode": True,
        "prediction_id": "test-uuid-1234"
    }
    output = PredictionOutput(**valid_data)
    assert output.species == SpeciesEnum.SETOSA
    assert output.confidence == 0.95
    assert output.needs_review is False
    
    # Invalid confidence should raise ValidationError
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["confidence"] = 1.5 # Should be <= 1.0
        PredictionOutput(**invalid_data)

def test_prediction_input_schema():
    from src.core.schemas import PredictionInput
    
    # Valid input should pass validation
    valid_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    input_data = PredictionInput(**valid_data)
    assert input_data.sepal_length == 5.1
    
    # Invalid sepal_length should raise ValidationError
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["sepal_length"] = 20.0 # Should be <= 15.0
        PredictionInput(**invalid_data)
