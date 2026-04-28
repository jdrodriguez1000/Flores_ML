import streamlit as st
from src.core.schemas import SpeciesEnum, FeedbackInput, PredictionOutput

def render_global_styles():
    """Inyecta el CSS avanzado del Design System 'The Clinical Sanctuary'."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
        
        /* Tipografía Base */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, .headline {
            font-family: 'Manrope', sans-serif;
            color: #00478d;
            letter-spacing: -0.02em;
        }
        
        /* Regla de No-Líneas: Capas Tonales */
        [data-testid="stAppViewContainer"] {
            background-color: #f8f9ff;
        }
        
        [data-testid="stSidebar"] {
            background-color: #f1f3fc;
            border-right: none;
        }

        /* Inputs Estilizados */
        .stNumberInput div[data-baseweb="input"] {
            background-color: #dfe2eb; /* surface-container-highest */
            border: none;
            border-radius: 0.5rem;
            padding: 4px;
        }
        
        .stNumberInput input {
            color: #181c22;
            font-weight: 500;
        }

        /* Botones con Gradientes Líquidos */
        .stButton button {
            background: linear-gradient(135deg, #00478d, #005eb8) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem 2rem !important;
            font-weight: 700 !important;
            font-family: 'Manrope', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            transition: all 0.2s ease !important;
            width: 100%;
        }
        
        .stButton button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 71, 141, 0.2);
        }

        /* Tarjeta de Resultados (Arquitectónica) */
        .result-card {
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 32px rgba(24,28,34,0.04);
            margin-top: 1.5rem;
        }

        /* Alertas Clínicas */
        .alert-clinical {
            padding: 1.5rem;
            border-radius: 0.75rem;
            display: flex;
            align-items: start;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .alert-success {
            background-color: #c8daff; /* on-primary-container lightened */
            color: #001b3d;
        }
        
        .alert-warning {
            background-color: #ffdbcb; /* tertiary-fixed */
            color: #793100;
        }

        .metric-value {
            font-family: 'Manrope', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            color: #00478d;
            line-height: 1;
        }
        
        .metric-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #424752;
            margin-bottom: 0.25rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renderiza el encabezado editorial."""
    st.title("Análisis de Muestras")
    st.markdown("""
    <p style="color: #424752; font-size: 1.1rem; max-width: 600px; line-height: 1.6;">
        Panel de control de precisión para la validación de parámetros botánicos en tiempo real. 
        Siga los protocolos institucionales de LabPrecision Sanctuary.
    </p>
    """, unsafe_allow_html=True)

def render_result_card(result: PredictionOutput, latency: float):
    """Renderiza la tarjeta de resultados con el estilo del Design System."""
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    if result.shadow_mode:
        st.info("Operación en Shadow Mode: Inferencia registrada para auditoría silenciosa.", icon="ℹ️")
    elif result.needs_review:
        st.markdown(f"""
        <div class="alert-clinical alert-warning">
            <div style="font-size: 1.5rem;">⚠️</div>
            <div>
                <div style="font-weight: 800; text-transform: uppercase;">Revisión Manual Requerida</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">
                    La muestra presenta una confianza de {result.confidence*100:.1f}%. Se requiere validación del analista.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-clinical alert-success">
            <div style="font-size: 1.5rem;">✅</div>
            <div>
                <div style="font-weight: 800; text-transform: uppercase;">Muestra Verificada</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">
                    Determinación automática completada con éxito.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="metric-label">Especie Determinada</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{result.species.value}</div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="metric-label">Confianza</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{result.confidence*100:.1f}%</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f1f3fc; font-size: 0.7rem; color: #727783; display: flex; justify-content: space-between;">
        <span>ID: {result.prediction_id}</span>
        <span>Latencia: {latency:.3f}s</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_feedback_loop(result: PredictionOutput, service):
    """Renderiza la sección de feedback loop."""
    st.divider()
    st.write("### ¿Es correcta la clasificación?")
    
    species_options = [s.value for s in SpeciesEnum]
    default_index = 0
    if result.species.value in species_options:
        default_index = species_options.index(result.species.value)
        
    manual_species = st.radio(
        "Especie Real", 
        options=species_options,
        index=default_index,
        help="Confirme la identidad biológica de la muestra."
    )
    
    if st.button("Registrar Corrección"):
        assert result.prediction_id is not None, "El ID de predicción no puede ser nulo para registrar feedback"
        feedback = FeedbackInput(
            prediction_id=result.prediction_id,
            manual_species=SpeciesEnum(manual_species),
            is_valid_sample=True,
            analyst_id="ANALYST-01"
        )
        if service.register_feedback(feedback):
            st.success("Feedback registrado con éxito")
        else:
            st.error("Fallo en la persistencia del feedback.")
