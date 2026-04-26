# Software Architecture Document (SAD) - Flores_ML

## 1. Introducción y Propósito
Este documento detalla la arquitectura técnica del sistema **Flores_ML**, diseñado para la clasificación automatizada de especies de flores con alta precisión y validación de seguridad. La arquitectura se basa en el principio de **Desacoplamiento Absoluto** entre la lógica de Machine Learning y la infraestructura de entrega.

## 2. Decisiones de Diseño Críticas
- **Arquitectura Hexagonal (Monolito Modular):** Se adopta para aislar el *Core* (ML y Reglas de Negocio) de los *Adaptadores* (API, UI, DB), facilitando el re-entrenamiento del modelo sin afectar la integridad del sistema.
- **Módulos Profundos (Deep Modules):** Las interfaces se diseñan para ocultar la complejidad interna del pipeline de datos y el modelo ML, exponiendo firmas simples para reducir el acoplamiento.
- **Fail-Fast & Unified Error Mapping:** Validación estricta en la frontera mediante Pydantic. Los errores se transforman en un esquema estándar `{error_code: str, message: str, detail: list}` para facilitar el consumo en el Frontend.
- **Centralized Configuration:** Uso obligatorio de una clase `Settings` (Pydantic Settings) para gestionar variables de entorno, rutas de modelos y parámetros de base de datos, garantizando inmutabilidad durante la ejecución.

## 3. Modelo C4

### 3.1. Nivel 1: Diagrama de Contexto
El **Analista de Laboratorio** interactúa con el **Flores_ML System** para ingresar medidas morfológicas y obtener clasificaciones certificadas. El sistema reporta el feedback al **Auditor de Calidad** y registra logs para el cumplimiento de KPIs.

### 3.2. Nivel 2: Diagrama de Contenedores
1.  **Dashboard (Streamlit):** Interfaz de usuario que consume la lógica del `core` mediante invocaciones directas (importación de módulos de Python) para el despliegue monolítico, permitiendo una latencia mínima.
2.  **Service API (FastAPI):** Puerta de enlace asíncrona que expone los servicios al exterior. Se despliega como un proceso independiente (puerto distinto) pero consumiendo la misma base de código (Core) que el Dashboard.
3.  **Inference Engine (Library):** Módulo interno que carga el pipeline de Scikit-Learn. Los artefactos (`.pkl`) se cargan en memoria al inicio para garantizar respuestas en < 100ms. Implementa **Hot-Swapping (Graceful Reload)**: la API podrá recargar un nuevo archivo `.pkl` en background mediante un endpoint protegido, reemplazando el modelo activo sin requerir reinicio del contenedor (Zero-Downtime).
4.  **Audit Store (SQLite):** Base de datos configurada con **Journal Mode = WAL** para permitir múltiples lectores y un escritor concurrente sin bloqueos de tabla.

## 4. Stack Tecnológico
| Componente | Tecnología | Justificación |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.12+ | Estándar de industria con tipado estricto para ML. |
| **Backend API** | FastAPI | Alto rendimiento asíncrono y validación nativa con Pydantic. |
| **Frontend** | Streamlit | Desarrollo acelerado de dashboards de datos en Python. |
| **Machine Learning** | Scikit-Learn | Robustez para datasets tabulares pequeños y soporte para matrices de costos. |
| **Persistencia** | SQLite (WAL Mode) | Manejo de concurrencia para auditoría y feedback loop. |
| **Containerización**| Docker | Garantiza paridad de entornos (Multi-stage build). |

## 5. Estrategias de Mitigación y Seguridad (Shields)

### 5.1. Target Leakage Shield (Capa de Datos)
Para cumplir con el Reporte de Factibilidad, todo proceso de ingesta y preprocesamiento en la capa *Silver* (`src/data/`) tiene la instrucción imperativa de **eliminar la columna `Id`**. Adicionalmente, el esquema de datos garantiza el **aislamiento estricto de la variable objetivo (`Species`)**, impidiendo que se cuele en el payload de características durante cualquier inferencia.

### 5.2. Virginica Shield (Capa de Negocio)
Dada la penalización 10:1 definida en el BRD, el sistema implementa un "Escudo de Virginica":
- Si la predicción es `Virginica` pero la confianza es **< 98%**, el sistema forzará el estado `needs_review=True`.
- La UI bloqueará la auto-aprobación en estos casos, requiriendo validación manual obligatoria.

### 5.3. Null Policy & Range Validation
- **Política de Nulos:** Hard Reject. Cualquier valor faltante dispara un error HTTP 400.
- **Rangos Biológicos:** Validación estricta de **0.1 cm a 15.0 cm** para todas las dimensiones (Sépalo/Pétalo).

### 5.4. Model Lineage & Metadata
Toda respuesta de inferencia debe incluir metadatos de trazabilidad:
- `model_version`: Hash o timestamp del artefacto cargado.
- `prediction_timestamp`: Momento exacto de la ejecución.
- `execution_time_ms`: Latencia medida para monitoreo de SLA.

### 5.5. Control de Acceso (RBAC Lite) e Inmutabilidad
El sistema gestionará dos roles básicos:
- **Analista:** Permiso de lectura e inserción de nuevas predicciones.
- **Auditor:** Permiso para visualizar el 5% de auditoría ciega y emitir correcciones de etiquetas.
*Inmutabilidad (Audit Trail):* La base de datos es de **Solo Adición (Append-Only)**. Las "sobreescrituras" de etiquetas por parte del Auditor no modifican el registro original, sino que insertan un nuevo registro vinculado con la etiqueta corregida, garantizando la trazabilidad histórica del error.
*Implementación:* Basada en identificadores de sesión y decoradores de acceso en la capa de servicios (Core).

## 6. Estructura del Repositorio (`src/` y `tests/`)
- `src/api/`: Adaptadores FastAPI y definición de endpoints.
- `src/core/`: Lógica de negocio, puertos (interfaces) y modelos Pydantic **(Regidos por el Data Contract)**.
- `src/data/`: Pipelines de ingesta (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) y mitigación de leakage.
- `src/model/`: Implementación del motor de inferencia y envoltorios del modelo ML.
- `src/ui/`: Aplicación Streamlit y componentes visuales.

### 6.1. Test Architecture (BDD & TDD)
La arquitectura de pruebas reflejará la estructura del código y garantizará el **BDD-as-DoD**:
- `tests/unit/`: Pruebas aisladas para lógica de datos (`src/data/`) e inferencia pura (`src/model/`).
- `tests/integration/`: Pruebas de interacción entre la API y el Core.
- `tests/e2e/`: Pruebas de interfaz completa, mapeadas directamente a los escenarios Gherkin de `behavior.md`.

## 7. Infraestructura y Despliegue
- El sistema operará inicialmente en **Shadow Mode** (`SHADOW_MODE=True`), ejecutando inferencias en segundo plano sin mostrarlas al usuario final. **Mutación de UI:** Durante este modo, la interfaz forzará al analista a ingresar su "Clasificación Manual" obligatoria para guardar el registro, permitiendo acumular el *ground truth* para certificar la IA (500 muestras).
- El feedback loop se activa al 100% para casos de baja confianza y al **5% aleatorio** para auditoría ciega de alta confianza.

---
**Arquitecto:** @ai-solutions-architect
**Fecha:** 26 de abril de 2026
**Estado:** ✅ CERTIFICADO TÉCNICO
