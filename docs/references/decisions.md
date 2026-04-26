# Registro de Decisiones y Lecciones Aprendidas - Flores_ML

---

## [2026-04-26] - Blindaje de Contrato de Datos (v1.8.0) y Resiliencia MLOps

**Fase Actual:** Fase 1: Discovery
**Contexto:** Auditoría extrema ("Devil's Advocate") y certificación final del `contract.md` y sincronización con `SpecDD.md` por el @ai-solutions-architect.

### ⚖️ Decisiones
1. **Blindaje de Unidades y Tipado en Disco (Parquet):** Se prohibió el uso de formatos planos (CSV/JSON) para las capas Silver y Gold. Se mandató el uso de **Parquet (Snappy)** para garantizar que el tipado estricto (`float64`, `SpeciesEnum`) y las unidades de medida (cm) se preserven físicamente en disco sin degradación.
2. **Implementación del "Virginica Shield" y Lógica de Inferencia:** Se formalizaron las reglas matemáticas para el campo `needs_review`. Se estableció una política asimétrica donde la clase `Virginica` requiere un **98% de confianza** para ser automatizada, elevando la seguridad operativa sobre la especie de mayor riesgo.
3. **Política de Frontera Estricta (Extra.forbid):** Se decidió rechazar cualquier petición API con campos adicionales o coerción de tipos (HTTP 422 - `ERR_07`). Esto cierra vectores de ataque por inyección de payload y garantiza que el sistema solo procese datos contractualmente válidos.
4. **Arquitectura Closed-Loop (Filtrado de Ruido):** Se integró el campo `is_valid_sample` en el Feedback Loop. Esto permite que el experto humano marque datos corruptos o ruidosos para que sean **ELIMINADOS** de la capa Gold, evitando el envenenamiento del dataset de reentrenamiento.
5. **Hashing Lógico Determinista para Linaje:** Se rechazó el hashing de archivos físicos por su volatilidad. Se mandató que el `data_version_hash` se calcule sobre el **contenido lógico de los datos**, garantizando que el linaje sea inmutable y reproducible independientemente de la infraestructura.
6. **Securización contra DoS y Inyección:** Se establecieron límites estrictos de longitud para `analyst_id` (50 caracteres) y validación de formato **UUIDv4** para `prediction_id`, blindando el repositorio de auditoría contra ataques de saturación de memoria.
7. **Soberanía del Tiempo (UTC-Only):** Se prohibió el uso de husos horarios locales. Todo evento de sistema debe grabarse en **UTC estricto**, eliminando discrepancias temporales en el análisis de derivas (Drift) entre servidores distribuidos.

### 💡 Lecciones Aprendidas (Learnings)
- **El CSV es el enemigo de la Calidad:** Confiar en archivos de texto para capas intermedias de datos destruye el tipado estricto definido en el código. El contrato de datos debe ser también un **Contrato de Almacenamiento**.
- **La API es una Frontera de Seguridad:** No basta con validar rangos biológicos; si la API es permisiva con campos extra, el sistema es vulnerable. El rigor del contrato de datos debe extenderse a la configuración del parser (Pydantic `Extra.forbid`).
- **El Linaje Físico es Engañoso:** Un mismo dataset guardado dos veces en Parquet puede tener hashes de archivo distintos. El linaje real reside en el dato, no en el contenedor.
- **El Ruido es Veneno:** Sin una flag de "Muestra Inválida" (`is_valid_sample`), el ciclo de feedback obliga al experto a categorizar basura como conocimiento, degradando el modelo con cada iteración de reentrenamiento.

---

## [2026-04-26] - Especificación Técnica Blindada (SpecDD) y Contratos de Datos

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de las tareas T-1.9 (SpecDD) y T-1.10 (Contrato de Datos). Refinamiento de interfaces bajo el rigor de "Módulos Profundos" y "Bala Trazadora" por el @ai-solutions-architect.

### ⚖️ Decisiones
1. **Orquestación mediante `PredictionService` (Core Logic):** Se rechazó colocar la lógica de negocio en los controladores de la API. Se creó un servicio orquestador (`PredictionService`) que coordina secuencialmente la limpieza (`DataProcessor`), la inferencia (`InferenceEngine`) y el registro de auditoría (`AuditRepository`), manteniendo los adaptadores "delgados" y testeables.
2. **Tipado Estricto con `SpeciesEnum`:** Para eliminar errores por "strings mágicos", se mandató el uso de un Enum para las especies en todos los contratos. Esto garantiza que el Frontend y el Backend hablen el mismo idioma tipado y facilita la validación en tiempo de compilación/linting.
3. **Interfaz Dual del `DataProcessor` (Single vs. Batch):** Se decidió que el procesador de datos soporte tanto registros individuales (API) como procesamiento por lotes (Pipeline de Ingesta). Esto permite reutilizar la lógica de **Leakage Shield** (drop `Id`) y validación biológica en ambas etapas del ciclo de vida del dato.
4. **Contrato de Error Unificado:** Se definió un esquema JSON de error estándar (`error_code`, `message`, `detail`) y una matriz de excepciones técnicas obligatorias. Esto permite que el agente de QA escriba tests exactos en la fase **RED** y que el Frontend maneje errores de forma elegante.
5. **Inyección de Dependencias para Mocking:** Se definió explícitamente la interfaz `MockInferenceEngine` para la **Bala Trazadora**. Esto habilita al equipo de ingeniería a construir toda la "tubería" (UI -> API -> DB) sin esperar a que el modelo real de ML esté entrenado.
6. **Validación de Rango en la Frontera:** Se mandató que los esquemas de Pydantic ejecuten la validación de rango (0.1 - 15.0 cm) en la frontera misma del sistema (entrada de la API), siguiendo el principio de *"Fail-Fast Design"*.

### 💡 Lecciones Aprendidas (Learnings)
- **El Peligro de los "Adaptadores Gordos":** Sin un `PredictionService`, la lógica de auditoría y validación se dispersa en los endpoints de FastAPI, haciendo casi imposible cambiar de framework web en el futuro sin reescribir la lógica de negocio.
- **La Bala Trazadora requiere Mocks Contractuales:** No basta con decir "usaremos un mock"; el mock debe tener su propia interfaz definida en el SpecDD para que el desarrollador no tenga que adivinar qué campos dummy devolver.
- **La Deuda Técnica del "Batch vs Single":** Olvidar la capacidad de procesamiento por lotes en el diseño inicial del `DataProcessor` obliga a duplicar código de limpieza en los scripts de ingesta. Un módulo profundo debe considerar todos los casos de uso del dato.

---

## [2026-04-26] - Arquitectura Hexagonal y Blindaje Sistémico (SAD)

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de la tarea T-1.8 (Software Architecture Document). Definición de la topología modular y el stack tecnológico bajo escrutinio de "Abogado del Diablo" por el @ai-solutions-architect.

### ⚖️ Decisiones
1. **Topología Monolito Modular (Hexagonal):** Se rechazó una arquitectura de microservicios para evitar sobrecarga operativa en la Fase 2, optando por un Monolito Modular. Se implementó la **Arquitectura Hexagonal** para aislar el núcleo de lógica de ML (`core`) de los adaptadores de entrega (`api`, `ui`), garantizando el mandato *"Decoupling is King"*.
2. **Dual-Process Deployment (FastAPI + Streamlit):** Tras detectar riesgos de bloqueos en el Event Loop, se decidió que FastAPI (API externa) y Streamlit (Dashboard) operen como procesos independientes con puertos distintos, pero compartiendo la misma base de código (`src/core/`). Esto garantiza estabilidad y escalabilidad independiente.
3. **Resiliencia con Hot-Swapping (Zero-Downtime):** Se mandató que el motor de inferencia soporte la recarga dinámica de archivos `.pkl` en caliente. Esto permite actualizar el modelo ML sin reiniciar los contenedores, asegurando la continuidad operativa del laboratorio.
4. **Inmutabilidad del Audit Trail (Append-Only):** Para cumplir con estándares regulatorios de Laboratorios Iris, se prohibió la edición de registros en SQLite. Las correcciones de los auditores se manejarán mediante **versionado (nuevos registros vinculados)**, preservando la historia original para auditoría forense.
5. **Estrategia de Persistencia WAL (Write-Ahead Logging):** Se activó el modo WAL en SQLite para mitigar bloqueos de base de datos durante escrituras concurrentes de feedback, un punto crítico detectado en la auditoría de estrés.
6. **Centralización de la Verdad (Pydantic Settings):** Se eliminó la dispersión de configuraciones obligando al uso de una clase `Settings` única y tipada, integrando validación de secretos y rutas desde el inicio.

### 💡 Lecciones Aprendidas (Learnings)
- **La Paradoja del Shadow Mode:** Se identificó que una "IA Silenciosa" es inútil si el sistema no captura simultáneamente la etiqueta manual del analista. El Shadow Mode requiere una mutación de la UI para forzar el *Ground Truth* humano como base de comparación.
- **Fricción de Servidores Web:** Intentar embeber Streamlit dentro de FastAPI (o viceversa) en un solo proceso es un antipatrón en Python. La separación de procesos con lógica compartida es la ruta más limpia para mantener la simplicidad del código.
- **El TDD requiere Arquitectura de Pruebas:** No basta con definir dónde va el código (`src/`); el SAD debe dictar la estructura de `tests/` para que los agentes de QA no improvisen la jerarquía de validación.

---

## [2026-04-26] - Diseño de Autor y Certificación de Experiencia (UAT)

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de las tareas T-1.6 (Mockup Visual) y T-1.7 (Aprobación UAT) por el @ai-ux-designer. Evolución de la interfaz de "Premium" a "Author Edition" para garantizar la adopción del usuario de negocio.

### ⚖️ Decisiones
1. **Adopción de Estética "Technical Luxury":** Se decidió rechazar layouts genéricos ("AI slop") en favor de una dirección de arte de lujo técnico. Se implementó una capa de ruido de grano (Noise Grain), animaciones escalonadas (staggered motion) y sombras ambientales para proyectar una imagen de precisión científica y solidez institucional.
2. **Pivotaje a Lenguaje Operativo (Negocio-Centric):** Se eliminaron todos los tecnicismos de la interfaz. Términos como "Inferencia IA", "Features" o "Shadow Mode" fueron sustituidos por **"Clasificar Muestra"**, **"Medidas de la Flor"** y **"Aprendizaje Silencioso"**, respectivamente, para eliminar barreras de entrada al analista.
3. **Dashboard de Alta Densidad con Navegación Lateral:** Se abandonó la navegación superior por una sidebar fija para permitir un flujo de trabajo multitarea entre la captura de datos (Análisis), la auditoría de discrepancias (Revisión Experta) y el registro histórico.
4. **Implementación de Bucle de Feedback Directo:** Se decidió que la "Corrección Manual" no sea una pantalla aparte, sino una transformación del panel de resultados en un editor dinámico. Esto permite al experto sobrescribir a la IA en un solo clic, capturando la discrepancia para futuros reentrenamientos.
5. **Certificación Vinculante (Contractual):** Se formalizó el diseño mediante el acta `docs/Phase_discovery/mockup.md`. Se estableció que cualquier cambio visual posterior a esta firma debe ser tratado mediante un **Control de Cambios (CC)**, protegiendo la fase de ingeniería de desviaciones estéticas.

### 💡 Lecciones Aprendidas (Learnings)
- **La Estética construye Confianza:** En entornos científicos, una interfaz "plana" se percibe como poco fiable. El texturizado y la profundidad física del "Diseño de Autor" aumentan la percepción de valor del modelo de IA subyacente.
- **La Percepción del Tiempo es Clave:** Se aprendió que una respuesta instantánea de la IA puede parecer "superficial" al usuario de negocio. Se exigió una latencia artificial de ~0.8s en la implementación final para simular un proceso de "análisis profundo" y aumentar la credibilidad del veredicto.
- **La Integridad del Prototipo es Innegociable:** Se identificó que simplificar vistas secundarias (Historial/Auditoría) durante la iteración de la vista principal confunde al stakeholder. El prototipo debe evolucionar como un bloque íntegro de experiencia en cada turno.

---

## [2026-04-26] - Auditoría de Factibilidad de Datos (Devil's Advocate)

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de la tarea T-1.5 (Data Feasibility Report). Evaluación profunda de la salud técnica y estadística de `data/Bronze/Iris.csv` por el @ai-data-auditor.

### ⚖️ Decisiones
1. **Eliminación Obligatoria de `Id` (Sanitización Crítica):** Se detectó una correlación crítica de 0.94 entre la columna `Id` y la variable objetivo (Target Leakage). Se decidió eliminar estrictamente esta columna en la capa Silver y aplicar un barajado (shuffling) determinista antes de cualquier partición de datos para destruir el sesgo de recolección.
2. **Validación Bootstrap vs. K-Fold:** Debido al tamaño microscópico de la muestra (150 registros) y al alto solapamiento (hasta 96%) entre Versicolor y Virginica, se decidió sustituir la validación K-Fold simple por **Bootstrap Resampling (1000 iteraciones)** para obtener intervalos de confianza estadísticamente sólidos y no depender de la suerte en una partición pequeña.
3. **Re-validación Ciega del Ground Truth (20%):** Ante la incertidumbre del linaje de los datos históricos y la variabilidad inter-analista reportada en el BRD, se ordenó someter el 20% del dataset a una re-validación ciega por un experto independiente para confirmar que las etiquetas actuales no contienen ruido.
4. **Stress Testing para Prior Drift:** Dado que el dataset está perfectamente balanceado (50/50/50) pero la realidad de producción podría no estarlo, se decidió exigir pruebas de estrés inyectando pesos de clase artificiales para simular flujos desbalanceados.
5. **Normalización Estricta de Esquema (Capa Silver):** Se identificó una desalineación crítica entre la nomenclatura cruda de Bronze (ej. `SepalLengthCm`, `Iris-setosa`) y el contrato BDD (`sepal_length`, `Setosa`). Se decidió que la capa Silver debe realizar esta normalización obligatoriamente para evitar que los tests TDD fallen por desajuste de diccionario.

### 💡 Lecciones Aprendidas (Learnings)
- **El Peligro de la "Calidad Técnica Perfecta":** Un dataset sin nulos, sin duplicados y dentro de rangos biológicos (10/10 técnico) puede esconder venenos mortales (Leakage y Solapamiento). La salud estadística es más crítica que la salud estructural.
- **La Trampa de las Muestras Pequeñas:** Con solo 50 registros por clase, fallar una sola predicción en el set de prueba destruye el F1-Score del 98% exigido por el negocio. Los KPIs agresivos sobre datasets pequeños requieren validaciones robustas (Bootstrap) para no vender "falsas esperanzas".
- **El Linaje es Verdad:** Asumir que las etiquetas de un CSV histórico son "Ground Truth" absoluto es ingenuo si el negocio reporta que los analistas se equivocan. El ruido en las etiquetas es el límite superior silencioso del Accuracy de cualquier modelo.

---

## [2026-04-26] - Blindaje y Mecanización del Contrato de Comportamiento (BDD)

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución y refinamiento de la tarea T-1.4 (Contrato de Comportamiento). Evolución del documento `behavior.md` de v1.0.0 a v1.3.0 bajo auditoría de "Abogado del Diablo".

### ⚖️ Decisiones
1. **Mecanización Absoluta del BDD (v1.3.0):** Se decidió prohibir el lenguaje abstracto en los pasos Gherkin (ej. "ingresa medidas válidas"). Ahora es obligatorio el uso de **Data Tables** con valores físicos reales para que los escenarios sean 100% traducibles a tests automatizados sin interpretación.
2. **Lógica de Seguridad "Virginica Shield":** Dado el costo 10:1 de error en la especie Virginica, se estableció un umbral de confianza reforzado del **98%** exclusivo para esta clase. Cualquier predicción de Virginica por debajo de este valor activará `needs_review=True`, ignorando el umbral global del 85%.
3. **Validación Ciega para Auditoría (5%):** Se definió que ante el trigger de auditoría aleatoria, el sistema no solo debe solicitar revisión, sino **ocultar la predicción de la IA** en la interfaz para garantizar que el etiquetado del analista sea independiente y sirva como Ground Truth puro.
4. **Estandarización de Errores 400:** Se fijó el esquema de respuesta para errores de validación (`error_detail` con campos `loc` y `msg`) para asegurar la interoperabilidad con el Frontend y permitir una depuración precisa en el dashboard.
5. **Shadow Mode via Feature Flag:** Se integró el comportamiento de "IA Silenciosa" mediante la variable `shadow_mode` en el contrato, permitiendo la recolección de datos de desempeño en producción sin afectar la operación actual.

### 💡 Lecciones Aprendidas (Learnings)
- **El Gherkin Abstracto es Deuda Técnica:** Las especificaciones vagas en BDD obligan al ingeniero de QA a inventar datos de prueba, lo que rompe la trazabilidad. Las tablas de datos son el "contrato de unidad" del comportamiento.
- **Sesgo de Confirmación (Oracle Bias):** Se identificó que mostrar la predicción de la IA durante una auditoría aleatoria sesga al analista. La validación ciega es la única métrica de salud real en MLOps.
- **Asimetría de Riesgo exige Asimetría de Lógica:** No todas las clases valen lo mismo. Aplicar un umbral de confianza único es un error financiero si una clase (Virginica) tiene un costo de error desproporcionadamente alto.

---

## [2026-04-26] - Certificación del BRD y Blindaje de Reglas de Negocio

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de la tarea T-1.3 (Business Requirements Document) y revisión exhaustiva "Abogado del Diablo".

### ⚖️ Decisiones
1. **Umbral Dinámico vs. KPI de Automatización:** Se decidió que el umbral de confianza del 85% sea dinámico durante el Shadow Mode para garantizar que las alertas de revisión manual no superen el 3% del total, priorizando el KPI de automatización operativa.
2. **Penalización Asimétrica (10:1):** Se estableció un peso de 10:1 para los errores relacionados con la especie Virginica, instruyendo al equipo de ML a optimizar agresivamente para evitar Falsos Positivos y Falsos Negativos en esta clase.
3. **Auditoría Aleatoria en Producción:** Se implementó una regla de enviar el 5% de las predicciones con alta confianza a revisión manual oculta para prevenir la degradación silenciosa (Data Drift) y medir el Accuracy real sin depender de quejas de clientes.
4. **Política de Nulos Estricta (Hard Reject):** Se prohibió la imputación de datos faltantes en inferencia. Incompletitud en las 4 variables morfológicas resultará en un error 400 inmediato.

### 💡 Lecciones Aprendidas (Learnings)
- **El Peligro de las Métricas Competitivas:** Definir un umbral de confianza fijo (85%) competía directamente con la promesa de negocio (97% de automatización). Hacer el umbral dependiente del KPI salvó al proyecto de un fallo operativo.
- **Ceguera de Producción:** Confiar únicamente en las alertas de baja confianza para el reentrenamiento crea un sesgo de supervivencia. La auditoría aleatoria (5%) es fundamental para conocer el estado real de salud del modelo en el mundo real.

---

## [2026-04-26] - Configuración de Identidad y Fuentes

**Fase Actual:** Fase 1: Discovery
**Contexto:** Ejecución de la tarea T-1.2 de configuración del proyecto.

### ⚖️ Decisiones
1. **Identidad del Proyecto:** Se formalizó el nombre como **Flores_ML** y el propietario como **Laboratorios Iris**.
2. **Fuentes de Verdad:** Se integró el ID de NotebookLM (`f2fadc1a-2a2a-4cf9-81a0-b848e3049b2a`) como el "Cerebro del Proyecto" para asegurar que todos los agentes consulten la misma base de conocimiento profundo.
3. **Estructura de Datos:** Se ratificó el uso del dataset Iris en `data/Bronze/Iris.csv` como la fuente primaria de entrenamiento.

### 💡 Lecciones Aprendidas (Learnings)
- **Zero-Assumptions Policy:** La consulta directa al stakeholder sobre el ID de NotebookLM evitó el uso de placeholders, garantizando la trazabilidad técnica desde el día 1.
- **Importancia del Shared Understanding:** El log de entendimiento previo (T-1.1) facilitó la extracción de la descripción del proyecto sin necesidad de preguntas redundantes.

---

## [2026-04-25] - Inicialización y Refinamiento de Gobernanza

**Fase Actual:** Fase 1: Discovery
**Contexto:** Configuración inicial del backlog de trabajo.

### ⚖️ Decisiones
1. **Idioma Operativo:** Se decidió utilizar el español para la redacción del backlog y documentos de gobernanza para asegurar la alineación con el contexto de negocio y la metodología base.
2. **Atomicidad de Mockups:** Se decidió separar la creación del HTML del proceso de aprobación UAT. Esto garantiza que no se avance a ingeniería sin una firma vinculante en `docs/Phase_discovery/mockup.md`, reduciendo el riesgo de retrabajo (Scope Creep).
3. **Exigencia Técnica en DoDs:** Se elevaron los estándares del Contrato de Datos para incluir obligatoriamente reglas de transformación y políticas de nulos desde el diseño, previniendo fallos en la integración del pipeline de la Fase 2.

### 💡 Lecciones Aprendidas (Learnings)
- **Riesgo de Cascada Oculta:** Al redactar el backlog, es tentador agrupar "Diseño y Aprobación". Sin embargo, bajo SpecDD, la aprobación es un evento de gobernanza independiente que genera un artefacto crítico (`mockup.md`).
- **Poder del Auditor Interno:** El ejercicio de "Abogado del Diablo" permitió identificar que el reporte de factibilidad no era accionable si solo diagnosticaba; la inclusión del "plan de mitigación" lo convierte en una herramienta de ingeniería.
