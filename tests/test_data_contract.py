import pytest
from src.data.transformation import DataProcessor
from src.core.exceptions import (
    RangeValidationError,
    NullInputError,
    LogicConsistencyError,
    SchemaValidationError
)

@pytest.fixture
def processor():
    return DataProcessor()

def test_valid_input_passes(processor):
    """Prueba el camino feliz con un payload válido."""
    valid_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    result = processor.process_input(valid_data)
    assert result is not None
    assert result["sepal_length"] == 5.1

def test_null_policy_rejects(processor):
    """3.1. Null Policy (Hard Reject)"""
    invalid_data = {
        "sepal_length": None,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    with pytest.raises(NullInputError):
        processor.process_input(invalid_data)

def test_range_validation_rejects(processor):
    """3.2. Range Validation (Biological Constraints)"""
    invalid_data = {
        "sepal_length": 16.0, # out of range
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    with pytest.raises(RangeValidationError):
        processor.process_input(invalid_data)

def test_logic_consistency_rejects(processor):
    """3.3. Cross-Feature Validation (Logical Consistency)"""
    # petal_width MUST be less than petal_length
    invalid_data_petal = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 2.0 # width > length
    }
    with pytest.raises(LogicConsistencyError):
        processor.process_input(invalid_data_petal)

    # sepal_width MUST be less than sepal_length
    invalid_data_sepal = {
        "sepal_length": 3.0,
        "sepal_width": 4.5, # width > length
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    with pytest.raises(LogicConsistencyError):
        processor.process_input(invalid_data_sepal)

def test_strict_payload_rejects_extra_fields(processor):
    """3.7. Política de Frontera Estricta (No Extra Fields)"""
    invalid_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "extra_field": "hacker"
    }
    with pytest.raises(SchemaValidationError):
        processor.process_input(invalid_data)

def test_strict_payload_rejects_coercion(processor):
    """3.7. Política de Frontera Estricta (No Coercion)"""
    invalid_data = {
        "sepal_length": "5.1", # String en vez de float
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    with pytest.raises(SchemaValidationError):
        processor.process_input(invalid_data)
