import time
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.core.schemas import PredictionInput, PredictionOutput, FeedbackInput
from src.core.service import PredictionService
from src.core.repository import AuditRepository
from src.models.inference import InferenceEngine
from src.data.transformation import DataProcessor
from src.core.config import Settings
from src.core.exceptions import (
    RangeValidationError,
    NullInputError,
    LogicConsistencyError,
    SchemaValidationError
)

app = FastAPI(title="Flores_ML API", version="1.3.0")

# Inicialización de dependencias
settings = Settings()
processor = DataProcessor()
engine = InferenceEngine(settings.MODEL_PATH)
repo = AuditRepository()
service = PredictionService(processor, engine, repo)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration * 1000.0,
        "client": request.client.host if request.client else "unknown",
        "event": "api_request"
    }
    print(json.dumps(log_data))
    return response

@app.exception_handler(RangeValidationError)
async def range_validation_exception_handler(request: Request, exc: RangeValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "ERR_01",
            "message": "Valores fuera de rango biológico (0.1 - 15.0 cm).",
            "detail": []
        },
    )

@app.exception_handler(NullInputError)
async def null_input_exception_handler(request: Request, exc: NullInputError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "ERR_04",
            "message": "Se detectaron valores nulos o vacíos.",
            "detail": []
        },
    )

@app.exception_handler(LogicConsistencyError)
async def logic_consistency_exception_handler(request: Request, exc: LogicConsistencyError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "ERR_05",
            "message": "Inconsistencia biológica (ej: ancho > largo).",
            "detail": []
        },
    )

@app.exception_handler(SchemaValidationError)
async def schema_validation_exception_handler(request: Request, exc: SchemaValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "ERR_07",
            "message": "Error de tipado estricto o esquema inválido.",
            "detail": []
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_code = "ERR_07"  # Default schema error
    message = "Error de validación en la petición."
    
    # Intentamos ser más específicos según el tipo de error de Pydantic
    for err in errors:
        err_type = err.get("type")
        if err_type in ("less_than_equal", "greater_than_equal"):
            error_code = "ERR_01"
            message = "Valores fuera de rango biológico (0.1 - 15.0 cm)."
            break
        if err_type in ("missing", "type_error.none.not_allowed", "value_error.missing"):
            error_code = "ERR_04"
            message = "Se detectaron valores nulos o vacíos."
            break
            
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST if error_code != "ERR_07" else status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": error_code,
            "message": message,
            "detail": errors
        },
    )

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "model_version": engine.get_version(),
        "shadow_mode": settings.SHADOW_MODE
    }

@app.post("/api/v1/predict", response_model=PredictionOutput)
async def predict(data: PredictionInput):
    # El service espera un dict para el processor.process_input por ahora
    # según vimos en src/data/transformation.py
    try:
        result = service.predict_and_audit(data)
        return result
    except Exception as e:
        # Si es una de nuestras excepciones ya manejadas por handlers, se relanza
        if isinstance(e, (RangeValidationError, NullInputError, LogicConsistencyError, SchemaValidationError)):
            raise e
        # Error genérico
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback")
async def feedback(data: FeedbackInput):
    success = service.register_feedback(data)
    if not success:
        raise HTTPException(status_code=500, detail="Fallo al registrar feedback.")
    return {"status": "success", "message": "Feedback registrado correctamente."}
