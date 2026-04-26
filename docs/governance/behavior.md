# Behavior Specifications (BDD Contract)
## Proyecto: Flores_ML

> **Documento:** Contrato de Comportamiento BDD
> **Versión:** 1.3.0
> **Estado:** Aprobado
> **Fecha:** 2026-04-26
> **Autor:** ai-business-strategist
> **Trazabilidad:** BRD v1.0.0 → behavior.md v1.3.0
> **Fuente de verdad para:** ai-data-qa-engineer (Phase Engineering) · ai-full-stack-sdet (Phase Delivery)

---

## Jerarquía de Especificación

BRD (Intención) → BDD (Comportamiento) → TDD (Corrección)

---

## Feature: Clasificación Automatizada de Especies de Flores

### US.1: Obtención de Clasificación Automática
Como analista, quiero ingresar medidas morfológicas en un dashboard para obtener una clasificación automática.

**Escenario: Clasificación exitosa de una Setosa (Camino Feliz)**
  Dado que el analista ingresa medidas válidas:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 5.1   |
    | sepal_width     | 3.5   |
    | petal_length    | 1.4   |
    | petal_width     | 0.2   |
  Cuando solicita la clasificación
  Entonces el sistema debe responder en menos de 3 segundos
  Y el resultado de la especie debe ser "Setosa"
  Y el score de confianza debe ser visible

**Escenario: Clasificación Crítica de Virginica (Especie de Alto Valor)**
  Dado que el analista ingresa medidas típicas de Virginica:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 6.3   |
    | sepal_width     | 3.3   |
    | petal_length    | 6.0   |
    | petal_width     | 2.5   |
  Cuando solicita la clasificación
  Entonces el sistema debe identificar la especie como "Virginica"
  Y el score de confianza debe ser superior al 98% (debido a la penalización 10:1)

---

### US.2: Validación de Confianza Operativa y Seguridad (Shield)
Como analista, quiero ver un score de confianza para saber si debo validar manualmente el resultado y evitar errores de alto costo.

**Escenario: Alerta de baja confianza para revisión manual**
  Dado que el analista ingresa medidas que generan ambigüedad en el modelo (ej. frontera Versicolor/Virginica):
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 6.0   |
    | sepal_width     | 2.5   |
    | petal_length    | 4.8   |
    | petal_width     | 1.6   |
  Cuando solicita la clasificación
  Entonces el sistema devuelve un score de confianza menor al 85%
  Y el dashboard debe mostrar una alerta visual de "Revisión Manual Requerida"
  Y el usuario debe ser instado a validar el resultado

**Escenario: Prevención de Falso Positivo en Virginica (Virginica Shield)**
  Dado que el analista ingresa medidas límite que el modelo predice como Virginica pero con confianza menor al 98%:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 6.0   |
    | sepal_width     | 2.7   |
    | petal_length    | 5.1   |
    | petal_width     | 1.8   |
  Cuando solicita la clasificación
  Entonces el sistema debe devolver "Virginica" como especie
  Pero el campo `needs_review` debe ser `True`
  Y el sistema NO debe permitir la auto-aprobación del registro, forzando el consenso manual

---

### US.3: Feedback Loop y Registro de Correcciones
Como auditor, quiero que el sistema guarde mi corrección manual cuando la IA falla o para fines de auditoría.

**Escenario: Registro de corrección manual por parte del analista**
  Dado que el sistema realizó una predicción con `needs_review` igual a `True`
  Cuando el analista selecciona manualmente la especie "Virginica" en el dashboard
  Y confirma la corrección
  Entonces el sistema debe persistir la entrada original junto con la etiqueta corregida "Virginica"
  Y debe confirmar al usuario mediante un mensaje que el feedback fue registrado para el reentrenamiento

**Escenario: Auditoría Aleatoria (5% Quality Control)**
  Dado que el analista ingresa medidas claras:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 5.1   |
    | sepal_width     | 3.5   |
    | petal_length    | 1.4   |
    | petal_width     | 0.2   |
  Y el trigger interno de auditoría aleatoria (5%) se evalúa como verdadero
  Cuando el analista solicita la clasificación
  Entonces el sistema debe devolver `needs_review` igual a `True` a pesar de la alta confianza
  Y el dashboard debe ocultar la predicción inicial de la IA, solicitando validación "ciega"

---

## Feature: Gestión de Ciclo de Vida y Despliegue (Mitigación)

**Escenario: Operación en Shadow Mode (IA Silenciosa)**
  Dado que el sistema tiene la variable de entorno `SHADOW_MODE=True`
  Y el analista ingresa medidas:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 5.1   |
    | sepal_width     | 3.5   |
    | petal_length    | 1.4   |
    | petal_width     | 0.2   |
  Cuando el analista guarda su clasificación manual
  Entonces el sistema debe ejecutar la inferencia de la IA en segundo plano
  Y la respuesta de la API debe devolver `shadow_mode` igual a `True`
  Y el dashboard NO debe mostrar el resultado de la IA al usuario

---

## Feature: Validación y Robustez de Datos (Contrato de Datos)

**Escenario: Validación de Límites Exactos (Edge Cases - Mínimo)**
  Dado que el analista ingresa medidas en el límite biológico inferior:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 0.1   |
    | sepal_width     | 0.1   |
    | petal_length    | 0.1   |
    | petal_width     | 0.1   |
  Cuando solicita la clasificación
  Entonces el sistema debe responder con estado 200 OK
  Y el resultado de la clasificación debe completarse sin errores de validación

**Escenario: Validación de Límites Exactos (Edge Cases - Máximo)**
  Dado que el analista ingresa medidas en el límite biológico superior:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 15.0  |
    | sepal_width     | 15.0  |
    | petal_length    | 15.0  |
    | petal_width     | 15.0  |
  Cuando solicita la clasificación
  Entonces el sistema debe responder con estado 200 OK
  Y el resultado de la clasificación debe completarse sin errores de validación

**Escenario: Rechazo de valores fuera de rango biológico (Extremos y Negativos)**
  Dado que el analista ingresa valores fuera de los rangos (0.1 - 15.0):
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 25.0  |
    | sepal_width     | -1.0  |
    | petal_length    | 1.4   |
    | petal_width     | 0.2   |
  Cuando solicita la clasificación
  Entonces el sistema debe rechazar la petición con un HTTP 400 Bad Request
  Y la respuesta JSON debe contener el campo `error_detail` indicando que `sepal_length` y `sepal_width` fallaron la validación
  Y no debe realizarse ninguna inferencia

**Escenario: Rechazo por valores nulos (Hard Reject)**
  Dado que el analista ingresa datos incompletos:
    | campo           | valor |
    |-----------------|-------|
    | sepal_length    | 5.1   |
    | sepal_width     | null  |
    | petal_length    | 1.4   |
    | petal_width     | 0.2   |
  Cuando solicita la clasificación
  Entonces el sistema debe rechazar la petición con un HTTP 400 Bad Request
  Y el mensaje en `error_detail` debe indicar que `sepal_width` es obligatorio

---

## Trazabilidad BDD → Criterios de Aceptación

| Escenario | US Origen | CA Relacionados |
| :--- | :--- | :--- |
| Clasificación exitosa (Setosa) | US.1 | Respuesta < 3s, Clasificación automática |
| Clasificación Crítica Virginica | BRD Sec 5 | Penalización 10:1, F1 > 98% |
| Alerta de baja confianza | US.2 | Score visible, Alerta si < 85% |
| Prevención Falso Positivo Virginica | BRD Sec 5 | Matriz de costos, Shielding |
| Registro de corrección manual | US.3 | Guardar corrección, Feedback Loop |
| Auditoría Aleatoria (5%) | BRD Sec 7.3 | QC aleatorio, Validación ciega |
| Operación en Shadow Mode | BRD Sec 7.1 | Feature Flag, Silencioso |
| Límites Exactos (0.1 / 15.0) | BRD Sec 3 | Range Validation, Edge Cases |
| Rechazo de valores inválidos | BRD Sec 3 | Rango 0.1 - 15.0 cm, Error 400 |

---

## Nota de Alineación con SpecDD

El tipo de retorno `PredictionResult` y el objeto de error de la API deben cumplir:
- `species`: String (Setosa, Versicolor, Virginica)
- `confidence`: Float (0.0 - 1.0)
- `needs_review`: Boolean (confidence < 0.85 OR (species == Virginica AND confidence < 0.98) OR random_audit_trigger)
- `error_detail`: List[Dict] (para errores 400, indicando `loc` y `msg`)
- `shadow_mode`: Boolean

Cualquier desviación de estos campos requerirá un Change Control.

