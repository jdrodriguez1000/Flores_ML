from src.core.schemas import PredictionInput, PredictionOutput, FeedbackInput
from src.core.repository import AuditRepository
from src.models.inference import InferenceEngine
from src.data.transformation import DataProcessor

class PredictionService:
    def __init__(self, processor: DataProcessor, engine: InferenceEngine, repo: AuditRepository):
        self.processor = processor
        self.engine = engine
        self.repo = repo

    def predict_and_audit(self, data: PredictionInput) -> PredictionOutput:
        """
        Flujo de Inferencia Web: 
        Process (Single) -> Predict -> Save Audit -> Return.
        """
        # 1. Procesar entrada (si fuera necesario aplicar transformaciones individuales)
        # El processor espera un dict para validaciones lógicas adicionales
        processed_dict = self.processor.process_input(data.model_dump())
        processed_data = PredictionInput(**processed_dict)
        
        # 2. Inferencia (Incluye Shielding y Audit Rate)
        output = self.engine.predict(processed_data)
        
        # 3. Guardar en Auditoría
        prediction_id = self.repo.save_prediction(data, output)
        output.prediction_id = prediction_id
        
        return output

    def register_feedback(self, feedback: FeedbackInput) -> bool:
        """Registra el feedback del analista."""
        return self.repo.update_feedback(feedback)
