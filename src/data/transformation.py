import pandas as pd
import warnings
from typing import Any
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from src.core.exceptions import (
    RangeValidationError, 
    NullInputError, 
    StatisticalDriftWarning,
    LogicConsistencyError,
    SchemaValidationError
)

class InputData(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    sepal_length: float = Field(ge=0.1, le=15.0)
    sepal_width: float = Field(ge=0.1, le=15.0)
    petal_length: float = Field(ge=0.1, le=15.0)
    petal_width: float = Field(ge=0.1, le=15.0)

    @model_validator(mode='after')
    def check_logic(self):
        if self.petal_width >= self.petal_length:
            raise ValueError("LogicConsistencyError")
        if self.sepal_width >= self.sepal_length:
            raise ValueError("LogicConsistencyError")
        return self

class DataProcessor:
    def process_input(self, data: Any) -> Any:
        """Validación de un solo registro (API). Se implementará con Pydantic."""
        if not isinstance(data, dict):
            raise SchemaValidationError()
            
        # Hard Reject for Nulls/NaNs
        for k, v in data.items():
            if v is None:
                raise NullInputError()
            if isinstance(v, float) and pd.isna(v):
                raise NullInputError()
                
        try:
            validated = InputData(**data)
        except ValidationError as e:
            for err in e.errors():
                err_type = err['type']
                if err_type in ('extra_forbidden', 'float_type', 'missing'):
                    raise SchemaValidationError()
                if err_type in ('less_than_equal', 'greater_than_equal'):
                    raise RangeValidationError()
                if err_type == 'value_error' and 'LogicConsistencyError' in err['msg']:
                    raise LogicConsistencyError()
            # Fallback
            raise SchemaValidationError()
            
        return validated.model_dump()

    def check_drift(self, df: pd.DataFrame, baseline_stats: dict) -> None:
        """
        Calcula el Z-score para cada columna contra el baseline.
        Dispara un StatisticalDriftWarning si Z-score > 3.
        """
        for col, stats in baseline_stats.items():
            if col in df.columns:
                mean_batch = df[col].mean()
                mean_base = stats["mean"]
                std_base = stats["std"]
                
                # Para prevenir división por cero en caso de std = 0
                if std_base == 0:
                    continue
                    
                z_score = abs(mean_batch - mean_base) / std_base
                if z_score > 3:
                    warnings.warn(
                        f"[ERR_06] Statistical drift detected in column '{col}' (Z-score = {z_score:.2f} > 3).",
                        StatisticalDriftWarning
                    )

    def process_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implementa el Leakage Shield para el pipeline de Ingesta:
        1. Drop 'Id'.
        2. Validación de rangos en todo el set.
        3. Normalización de nombres de columnas y especies.
        """
        # Columnas originales que contienen características morfológicas
        feature_cols = ['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']
        
        # 1. Null Policy (Hard Reject)
        # Verificamos si hay algún nulo en las características morfológicas
        if df[feature_cols].isnull().any().any():
            raise NullInputError()
            
        # 2. Range Validation (Biological Constraints)
        # Verificamos si algún valor está fuera del rango [0.1, 15.0]
        out_of_bounds = ((df[feature_cols] < 0.1) | (df[feature_cols] > 15.0)).any().any()
        if out_of_bounds:
            raise RangeValidationError()
            
        # 3. Mapeo y Normalización (Bronze -> Silver)
        df_silver = df.copy()
        
        # DESCARTAR (Leakage Shield)
        if 'Id' in df_silver.columns:
            df_silver = df_silver.drop(columns=['Id'])
            
        # Renombrar columnas
        rename_map = {
            'SepalLengthCm': 'sepal_length',
            'SepalWidthCm': 'sepal_width',
            'PetalLengthCm': 'petal_length',
            'PetalWidthCm': 'petal_width',
            'Species': 'species'
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        # Normalización de Target (SpeciesEnum)
        # Convierte "Iris-setosa" a "Setosa", etc.
        if 'species' in df_silver.columns:
            df_silver['species'] = df_silver['species'].str.replace('Iris-', '', regex=False).str.capitalize()
            
        return df_silver
