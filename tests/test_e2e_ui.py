import re
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_ui_successful_classification_setosa(page: Page):
    """
    Test E2E de Interfaz de Predicción - Camino Feliz (Setosa)
    Escenario: Clasificación exitosa de una Setosa (Camino Feliz)
    """
    # 1. Navegar al dashboard
    page.goto("http://localhost:8504")
    
    # Esperar a que la aplicación cargue (Streamlit muestra un loading screen inicial)
    expect(page.get_by_text("Parámetros", exact=True)).to_be_visible(timeout=15000)

    # 2. Ingresar medidas válidas
    # Streamlit encapsula los number inputs bajo esta clase
    inputs = page.locator(".stNumberInput input")
    inputs.nth(0).fill("5.1")
    inputs.nth(1).fill("3.5")
    inputs.nth(2).fill("1.4")
    inputs.nth(3).fill("0.2")

    # Streamlit puede requerir presionar Enter o perder el foco para registrar el cambio
    inputs.nth(3).press("Enter")

    # 3. Solicitar clasificación
    page.locator('button:has-text("Clasificar")').click()

    # 4. Resultado visible
    # Debe responder en menos de 3 segundos y mostrar Setosa y la confianza
    expect(page.get_by_text("Muestra Verificada")).to_be_visible(timeout=10000)
    
    # Usamos .first para evitar conflicto con los radio buttons del feedback loop
    expect(page.get_by_text("Setosa", exact=False).first).to_be_visible(timeout=5000)
    expect(page.get_by_text(re.compile(r"Confianza|Score|%", re.IGNORECASE)).first).to_be_visible()

@pytest.mark.e2e
def test_ui_manual_feedback_loop(page: Page):
    """
    Test E2E de Feedback Loop - Registro de corrección manual
    Escenario: Registro de corrección manual por parte del analista
    """
    # 1. Navegar al dashboard
    page.goto("http://localhost:8504")
    expect(page.get_by_text("Parámetros", exact=True)).to_be_visible(timeout=15000)

    # 2. Ingresar medidas de "Virginica Shield"
    # Valores: 6.0, 2.7, 5.1, 1.8 (Activan needs_review por ser Virginica con baja confianza)
    inputs = page.locator(".stNumberInput input")
    inputs.nth(0).fill("6.0")
    inputs.nth(1).fill("2.7")
    inputs.nth(2).fill("5.1")
    inputs.nth(3).fill("1.8")
    inputs.nth(3).press("Enter")

    # 3. Solicitar clasificación
    page.get_by_role("button", name="Clasificar").click()

    # 4. Verificación del Escudo (Shield)
    # Debe mostrar la alerta de revisión manual definida en el Design System
    expect(page.get_by_text("Revisión Manual Requerida")).to_be_visible(timeout=5000)

    # 5. Simulación de Feedback (Pasos que deben fallar - RED)
    # El analista debe poder seleccionar la especie real para corregir/confirmar
    # Buscamos por el texto esperado en la futura sección de feedback
    expect(page.get_by_text("¿Es correcta la clasificación?")).to_be_visible(timeout=2000)
    
    # Seleccionar la especie correcta
    # Nota: Este paso fallará porque el radio/select no existe aún
    page.get_by_label("Especie Real").click() 
    
    # 6. Registrar Corrección
    # Este botón tampoco existe todavía
    page.get_by_role("button", name="Registrar Corrección").click()

    # 7. Verificación final de éxito
    expect(page.get_by_text("Feedback registrado con éxito")).to_be_visible()
