import streamlit as st
import time

from src.core.config import Settings
from src.core.schemas import PredictionInput
from src.core.repository import AuditRepository
from src.models.inference import InferenceEngine
from src.data.transformation import DataProcessor
from src.core.service import PredictionService
from src.ui.components import (
    render_global_styles, 
    render_header, 
    render_result_card, 
    render_feedback_loop
)

# 1. Configuración de página e Inyección de CSS (Design System)
st.set_page_config(
    page_title="LabPrecision Sanctuary",
    page_icon="🔬",
    layout="wide"
)

# Inicializar estado para persistencia de resultados (Feedback Loop)
if "last_result" not in st.session_state:
    st.session_state.last_result = None

render_global_styles()

# 2. Inicialización de Servicios Core (Arquitectura Monolítica)
@st.cache_resource
def get_service():
    settings = Settings()
    processor = DataProcessor()
    engine = InferenceEngine(model_path=settings.MODEL_PATH)
    repo = AuditRepository(settings.DB_PATH)
    return PredictionService(processor=processor, engine=engine, repo=repo), settings

service, settings = get_service()

# 3. Construcción del Dashboard
render_header()

# Maquetación principal (Gutter editorial a la derecha)
col1, col2, col3 = st.columns([4, 6, 2])

with col1:
    st.subheader("Parámetros")
    with st.container():
        # Los labels deben coincidir exactamente con los requeridos por el test E2E y el Contrato de Datos
        sepal_length = st.number_input("sepal_length", min_value=0.1, max_value=15.0, value=5.1, step=0.1)
        sepal_width = st.number_input("sepal_width", min_value=0.1, max_value=15.0, value=3.5, step=0.1)
        petal_length = st.number_input("petal_length", min_value=0.1, max_value=15.0, value=1.4, step=0.1)
        petal_width = st.number_input("petal_width", min_value=0.1, max_value=15.0, value=0.2, step=0.1)
        
        submit = st.button("Clasificar")

with col2:
    st.subheader("Resultado de Determinación")
    
    if submit:
        with st.spinner("Analizando parámetros..."):
            try:
                # Armar el Payload
                input_data = PredictionInput(
                    sepal_length=sepal_length,
                    sepal_width=sepal_width,
                    petal_length=petal_length,
                    petal_width=petal_width
                )
                
                # Invocar Core Service
                start_time = time.time()
                result = service.predict_and_audit(input_data)
                latency = time.time() - start_time
                
                # Persistir resultado en sesión para Feedback
                st.session_state.last_result = result
                st.session_state.last_latency = latency

            except Exception as e:
                st.error(f"Error de Validación: {str(e)}")
                st.session_state.last_result = None

    # Renderizar Resultados y Feedback desde el Estado
    if st.session_state.last_result:
        result = st.session_state.last_result
        latency = getattr(st.session_state, "last_latency", 0.0)
        
        # Componentes Modulares del Design System
        render_result_card(result, latency)
        
        if not result.shadow_mode:
            render_feedback_loop(result, service)
            
    elif not submit:
        st.info("Ingrese los parámetros y presione 'Clasificar' para iniciar la determinación.", icon="🧪")

with col3:
    # Gutter vacío para balance editorial conforme a DESIGN.md
    pass
