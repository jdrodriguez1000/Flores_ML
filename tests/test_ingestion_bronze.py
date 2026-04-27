import pandas as pd
import pytest
import os
from src.data.ingestion import load_bronze_data

def test_bronze_ingestion():
    """T-2.1.1.A.RED: Test fallando para lectura de Iris.csv y validación de tipos base."""
    # Arrange
    csv_path = "data/Bronze/Iris.csv"
    
    # Asegurarnos de que el archivo existe antes de probar la función
    assert os.path.exists(csv_path), "El archivo Iris.csv no existe en la ruta esperada."

    # Act
    df = load_bronze_data(csv_path)

    # Assert
    assert isinstance(df, pd.DataFrame), "load_bronze_data debe retornar un DataFrame"
    assert not df.empty, "El DataFrame no debe estar vacío"
    
    expected_columns = ["Id", "SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm", "Species"]
    assert list(df.columns) == expected_columns, "Las columnas del DataFrame no coinciden con las esperadas"
    
    # Validar tipos base
    assert pd.api.types.is_integer_dtype(df["Id"]), "La columna Id debe ser integer"
    assert pd.api.types.is_float_dtype(df["SepalLengthCm"]), "La columna SepalLengthCm debe ser float"
    assert pd.api.types.is_float_dtype(df["SepalWidthCm"]), "La columna SepalWidthCm debe ser float"
    assert pd.api.types.is_float_dtype(df["PetalLengthCm"]), "La columna PetalLengthCm debe ser float"
    assert pd.api.types.is_float_dtype(df["PetalWidthCm"]), "La columna PetalWidthCm debe ser float"
    assert pd.api.types.is_object_dtype(df["Species"]) or pd.api.types.is_string_dtype(df["Species"]), "La columna Species debe ser object o string"

def test_bronze_lineage_registration():
    """T-2.1.1.LIN.RED: Test de Registro de Linaje (hash, timestamp)."""
    # Arrange
    csv_path = "data/Bronze/Iris.csv"
    assert os.path.exists(csv_path), "El archivo Iris.csv no existe en la ruta esperada."

    # Act
    df = load_bronze_data(csv_path)

    # Assert
    assert "lineage" in df.attrs, "El DataFrame no contiene metadatos de linaje ('lineage' en df.attrs)"
    lineage = df.attrs["lineage"]
    assert "hash" in lineage, "El linaje no contiene el hash del archivo de origen"
    assert "timestamp" in lineage, "El linaje no contiene el timestamp de ingesta"
    assert isinstance(lineage["hash"], str) and len(lineage["hash"]) > 0, "El hash debe ser un string válido"
    assert isinstance(lineage["timestamp"], str) or hasattr(lineage["timestamp"], "timestamp"), "El timestamp debe ser una fecha/hora válida"
