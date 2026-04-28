import streamlit as st
import time

from src.core.config import Settings
from src.core.schemas import PredictionInput, PredictionOutput, FeedbackInput, SpeciesEnum
from src.core.repository import AuditRepository
from src.models.inference import InferenceEngine
from src.data.transformation import DataProcessor
from src.core.service import PredictionService

# 1. Configuración de página e Inyección de CSS (Design System)
st.set_page_config(
    page_title="LabPrecision Sanctuary",
    page_icon="🔬",
    layout="wide"
)

# Inicializar estado para persistencia de resultados (Feedback Loop)
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Manrope', sans-serif;
        color: #00478d;
        letter-spacing: -0.02em;
    }
    
    /* No-Line Rule & Surface Layering */
    div[data-testid="stSidebar"] {
        background-color: #f1f3fc;
        border-right: none;
    }
    
    .stNumberInput input {
        background-color: #ffffff;
        border: none;
        border-radius: 0.25rem;
        padding: 0.75rem;
        box-shadow: 0 2px 8px rgba(24, 28, 34, 0.04);
    }
    
    .stNumberInput input:focus {
        box-shadow: 0 0 0 2px #00478d;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #00478d, #005eb8);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Manrope', sans-serif;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    /* Result Card Styling */
    .result-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 32px rgba(24,28,34,0.04);
        margin-top: 1rem;
    }
    
    .alert-amber {
        background-color: #9f4300;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 2. Inicialización de Servicios Core (Arquitectura Monolítica)
@st.cache_resource
def get_service():
    settings = Settings()
    processor = DataProcessor()
    # Para el tracer bullet de UI, asumo que el modelo ya existe. Si no, InferenceEngine debe manejar la inicialización correcta.
    engine = InferenceEngine(model_path=settings.MODEL_PATH)
    repo = AuditRepository(settings.DB_PATH)
    return PredictionService(processor=processor, engine=engine, repo=repo), settings

service, settings = get_service()

# 3. Construcción del Dashboard
st.title("Análisis de Muestras")
st.markdown("Panel de control de precisión para la validación de parámetros botánicos en tiempo real.")

# Maquetación principal (Gutter editorial a la derecha)
col1, col2, col3 = st.columns([4, 6, 2])

with col1:
    st.subheader("Parámetros")
    with st.container():
        # Los labels deben coincidir exactamente con los requeridos por el test E2E y el Contrato de Datos (0.1 a 15.0)
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
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        if result.shadow_mode:
            st.info("El sistema está operando en Shadow Mode (IA Silenciosa). Su inferencia ha sido registrada para auditoría.", icon="ℹ️")
        else:
            if result.needs_review:
                st.markdown(f'<div class="alert-amber">⚠️ Revisión Manual Requerida</div>', unsafe_allow_html=True)
                st.warning(f"La predicción inicial requiere confirmación. (Score: {result.confidence * 100:.1f}%)")
            else:
                st.success(f"**Muestra Verificada**")
                st.metric(label="Especie Determinada", value=result.species)
                st.metric(label="Confianza (Score %)", value=f"{result.confidence * 100:.1f}%")
                
            st.caption(f"ID Predicción: {result.prediction_id} | Latencia API: {latency:.3f}s")
            
            # --- SECCIÓN DE FEEDBACK LOOP ---
            st.divider()
            st.write("### ¿Es correcta la clasificación?")
            
            # Selector de Especie Real
            # Pre-seleccionar la especie predicha si no es Virginica Shield
            default_index = 0
            species_options = [s.value for s in SpeciesEnum]
            if result.species in species_options:
                default_index = species_options.index(result.species)
                
            manual_species = st.radio(
                "Especie Real", 
                options=species_options,
                index=default_index,
                help="Seleccione la especie confirmada biológicamente."
            )
            
            if st.button("Registrar Corrección"):
                feedback = FeedbackInput(
                    prediction_id=result.prediction_id,
                    manual_species=SpeciesEnum(manual_species),
                    is_valid_sample=True,
                    analyst_id="ANALYST-01"
                )
                if service.register_feedback(feedback):
                    st.success("Feedback registrado con éxito")
                else:
                    st.error("Error al registrar el feedback en la base de datos.")

        st.markdown('</div>', unsafe_allow_html=True)
    elif not submit:
        st.info("Ingrese los parámetros y presione 'Clasificar' para iniciar la determinación.", icon="🧪")


with col3:
    # Gutter vacío para balance editorial
    pass
