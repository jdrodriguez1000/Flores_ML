import pandas as pd
import hashlib
from datetime import datetime

def compute_file_hash(filepath: str) -> str:
    """Calcula el hash SHA-256 de un archivo."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_bronze_data(csv_path: str) -> pd.DataFrame:
    """
    Carga de datos crudos (Bronze layer) sin transformación de negocio.
    Garantiza la lectura fiel del archivo de origen.
    """
    df = pd.read_csv(csv_path)
    
    # Casting explícito para asegurar cumplimiento del contrato Bronze/Ingesta
    df["Id"] = df["Id"].astype(int)
    df["SepalLengthCm"] = df["SepalLengthCm"].astype(float)
    df["SepalWidthCm"] = df["SepalWidthCm"].astype(float)
    df["PetalLengthCm"] = df["PetalLengthCm"].astype(float)
    df["PetalWidthCm"] = df["PetalWidthCm"].astype(float)
    df["Species"] = df["Species"].astype(str)
    
    # Registro de linaje
    df.attrs["lineage"] = {
        "hash": compute_file_hash(csv_path),
        "timestamp": datetime.now().isoformat()
    }
    
    return df
