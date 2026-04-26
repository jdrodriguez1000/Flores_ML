# Business Requirements Document (BRD) - Flores_ML

## 1. Visión General del Proyecto
**Nombre del Proyecto:** Flores_ML (Sistema de Clasificación de Flores Automatizado)
**Objetivo Primario:** Implementar un sistema de clasificación basado en Inteligencia Artificial para estandarizar el proceso de etiquetado de flores en Laboratorios Iris, reduciendo la variabilidad inter-analista y eliminando la necesidad de validaciones redundantes (reprocesos).

## 2. Definición del Problema de Negocio
Actualmente, los analistas clasifican las flores manualmente basándose en medidas morfológicas. Este proceso es subjetivo y propenso a errores, lo que resulta en:
- **150 reprocesos mensuales** (15% del volumen total).
- **187 horas hombre/mes** de tiempo experto perdido en consensos de validación.
- **Pérdida de credibilidad** ante clientes finales debido a clasificaciones inconsistentes.

## 3. Traducción Técnica (ML Framing)
| Atributo | Especificación Técnica |
| :--- | :--- |
| **Tipo de Tarea** | Clasificación Supervisada Multi-clase |
| **Variable Objetivo ($y$)** | Especie de Flor (Setosa, Versicolor, Virginica) |
| **Variables de Entrada ($X$)** | Longitud Sépalo, Ancho Sépalo, Longitud Pétalo, Ancho Pétalo |
| **Rango de Validación** | **0.1 cm a 15.0 cm** (Valores fuera de rango disparan error 400). |
| **Política de Nulos** | **Estricta (Hard Reject).** No se permite imputación. Rechazar inferencia si falta un valor. |
| **Dataset de Referencia** | Iris Dataset (Robert Fisher) - 150 registros validados |

## 4. Arquitectura de KPIs y Métricas de Éxito
Para considerar el proyecto como exitoso, el sistema debe cumplir con los siguientes umbrales:

### 4.1. Métricas de Negocio (KPIs)
- **Reducción de Reprocesos:** $\ge$ 80% (Bajar de 150 a máximo 30 casos/mes).
- **Automatización Efectiva:** El sistema debe operar de forma autónoma en al menos el **97%** de los casos mensuales.

### 4.2. Métricas Técnicas (Model QA)
- **Global Accuracy:** $> 96\%$.
- **F1-Score (Especie Virginica):** $> 98\%$ (Debido a su alta sensibilidad comercial).
- **Umbral de Confianza Operativo:** $\ge 85\%$. 
    - *Nota:* Este umbral es dinámico y se ajustará durante el Shadow Mode para garantizar el cumplimiento del KPI de Automatización (máximo 3% de revisiones manuales).

## 5. Análisis del Costo del Error
El negocio ha definido una **Penalización Simétrica Crítica** para la especie **Virginica**:
- **Falso Positivo (Virginica):** Clasificar una flor común como "de alto valor" genera un reproceso crítico.
- **Falso Negativo (Virginica):** Omitir una flor de alto valor impacta en ingresos y reputación.
- **Acción:** El modelo debe optimizar mediante una matriz de costos con un **peso de penalización de 10:1** para cualquier error que involucre a la clase Virginica.

## 6. Requerimientos de Usuario (User Stories)
| ID | User Story | Criterio de Aceptación |
| :--- | :--- | :--- |
| **US.1** | Como analista, quiero ingresar medidas morfológicas en un dashboard para obtener una clasificación automática. | Interfaz con 4 inputs numéricos y respuesta en < 3 segundos. |
| **US.2** | Como analista, quiero ver un score de confianza para saber si debo validar manualmente el resultado. | Visualización clara de % de confianza y alerta si es < 85%. |
| **US.3** | Como auditor, quiero que el sistema guarde mi corrección manual cuando la IA falla. | El dashboard debe permitir al usuario sobreescribir la clasificación en cualquier momento, registrando la corrección para reentrenamiento. |

## 7. Estrategia de Despliegue y Mitigación
1. **Shadow Mode:** El sistema operará oculto inicialmente. La certificación requiere un **mínimo de 500 predicciones** con una correlación >96% contra el etiquetado manual antes de pasar a Fase Activa.
2. **Feature Flag:** La activación de la visualización de la IA solo ocurrirá tras la certificación del Shadow Mode.
3. **Feedback Loop y Auditoría:** Para medir el Accuracy real en producción sin sesgos, el sistema enviará aleatoriamente un **5% de las predicciones de alta confianza** a revisión manual (Auditoría de Calidad). Reentrenamiento mensual obligatorio del modelo o si el Accuracy cae por debajo del 94% durante 3 días consecutivos.

## 8. Aprobación
**Responsable:** @ai-business-strategist
**Fecha:** 26 de abril de 2026
**Estatus:** ✅ CERTIFICADO BLINDADO (Listo para Phase Engineering)
