# Acta de Certificación de Interfaz (Mockup UAT) - Flores_ML

> **Documento:** Certificación de Prototipo Visual (T-1.7)
> **Versión:** 1.0.0
> **Estado:** PENDIENTE DE FIRMA (Validado por ai-ux-designer)
> **Fecha:** 26 de abril de 2026
> **Referencia Técnica:** `mockup/index.html` (Author Edition)

## 1. Resumen Ejecutivo
Este documento formaliza la aprobación de la interfaz de usuario para el sistema **Flores_ML**. El prototipo adjunto ha sido diseñado bajo la estética de **"Technical Luxury & Scientific Precision"** y cumple con los requerimientos operativos del Dr. Robert Fisher (Stakeholder Principal).

## 2. Alcance de la Experiencia (User Stories Validadas)
El mockup integra y valida visualmente las siguientes capacidades:

| Escenario | Componente Visual | Validación de Negocio |
| :--- | :--- | :--- |
| **Captura Operativa** | Formulario de 4 medidas (cm) | Uso de lenguaje no técnico y rangos de 0.1 a 15.0 cm. |
| **Predicción en Tiempo Real** | Panel de resultados dinámico | Feedback visual inmediato con score de seguridad (%). |
| **Bucle de Feedback** | Botón "Corregir Manualmente" | Capacidad del experto para sobrescribir a la IA. |
| **Auditoría Ciega** | Caso "Control Calidad 5%" | Ocultamiento de la sugerencia IA para evitar sesgos. |
| **Protección de Valor** | Alerta "Especie Crítica" | Bloqueo de seguridad para validación humana de *Virginica*. |
| **Trazabilidad** | Registro de Día con Detalles | Desglose de medidas físicas por cada registro histórico. |

## 3. Especificaciones Estéticas (Author Edition)
La interfaz aprobada debe mantener estrictamente estas directrices en su implementación final:
*   **Texturizado:** Uso obligatorio de una capa de ruido sutil (Grain Overlay) para eliminar la planitud digital.
*   **Movimiento:** Animaciones escalonadas (`staggered entry`) para la entrada de datos y resultados.
*   **Profundidad:** Sombras ambientales de gran difuminado (Ambient Shadows) en lugar de bordes sólidos.
*   **Tipografía:** Manrope (Titulares) e Inter (Cuerpo de datos).

## 4. Compromisos Técnicos para Phase Engineering
1.  **Reactividad:** El `ai-frontend-engineer` debe replicar el flujo de "Procesando..." de 0.8s para mantener la percepción de cálculo profundo.
2.  **Shadow Mode:** La interfaz debe ser capaz de ocultar el panel de resultados totalmente cuando la variable `SHADOW_MODE` sea `True`.
3.  **Móvil:** Aunque el mockup es desktop-first (Laboratorio), la implementación debe ser responsiva conservando el sidebar.

## 5. Aprobación Stakeholder
Al marcar esta tarea como DONE en el backlog, el Stakeholder acepta que este diseño es el compromiso final de experiencia. Cualquier cambio posterior requerirá un **Change Control (CC)**.

---
**Diseñado por:** @ai-ux-designer
**Firma de Conformidad:** ____________________ (Usuario)
