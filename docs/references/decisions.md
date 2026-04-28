# Registro de Decisiones y Lecciones Aprendidas - Flores_ML

---

## [2026-04-26] - Implementación de Linaje Inmutable (Slice 1: Bronze)

**Fase Actual:** Fase 2: Ingeniería y Modelado
**Contexto:** Ejecución de las tareas `T-2.1.1.LIN.RED` y `T-2.1.1.LIN.GRN` para garantizar la trazabilidad técnica.

### ⚖️ Decisiones
1. **Persistencia de Metadatos vía `df.attrs`:** Se decidió utilizar el diccionario `attrs` de Pandas para almacenar el linaje técnico (`hash` y `timestamp`). Esto cumple con la regla de oro **"Bronze is Sacred"**, ya que permite adjuntar metadatos de gobernanza al objeto de datos sin alterar el esquema (columnas) original del CSV.
2. **Hashing de Archivo SHA-256:** Se implementó el cálculo del hash SHA-256 sobre el archivo físico en el momento de la ingesta. Esta es la "huella dactilar" digital que garantiza que los datos procesados corresponden exactamente al archivo fuente en el disco, permitiendo auditorías de integridad futuras.
3. **Timestamp de Ingesta en ISO 8601:** Se estandarizó el registro del tiempo de ingesta en formato string ISO 8601, facilitando la interoperabilidad con sistemas externos y garantizando la trazabilidad temporal del linaje.

### 💡 Lecciones Aprendidas (Learnings)
- **Metadatos no intrusivos:** `df.attrs` es la herramienta ideal para la gobernanza en capas tempranas; evita la tentación de añadir columnas "técnicas" que complican la lógica de limpieza posterior y mantienen el contrato de datos limpio.
- **TDD para Gobernanza:** Escribir el test de linaje antes que la implementación (`LIN.RED`) obligó a definir exactamente qué campos de metadatos eran necesarios, evitando el exceso de información (over-engineering) en la capa Bronze.

---

## [2026-04-26] - Implementación de Limpieza Silver y Calidad de Código (Slice 1)

**Fase Actual:** Fase 2: Ingeniería y Modelado
**Contexto:** Ejecución de `T-2.1.1.B.RED`, `T-2.1.1.B.GRN` y `T-2.1.1.REF`.

### ⚖️ Decisiones
1. **Jerarquía de Excepciones de Dominio:** Se implementó una clase base `AppError` y excepciones específicas (`RangeValidationError`, `NullInputError`) con códigos de error estandarizados (`ERR_01`, `ERR_04`). Esto permite una gestión de errores predecible tanto en el pipeline de datos como en la futura API.
2. **Normalización Agresiva de Categorías:** Se decidió limpiar la columna `species` eliminando el prefijo `"Iris-"` y aplicando capitalización. Esto asegura la paridad total con el `SpeciesEnum` definido en el SpecDD, eliminando inconsistencias de nombres desde la capa Silver.
3. **Refuerzo del Leakage Shield:** La eliminación de la columna `Id` se movió al `DataProcessor` para asegurar que ningún registro procesado para entrenamiento o inferencia contenga identificadores que puedan causar sobreajuste o fuga de información.
4. **Tipado Estático Obligatorio en Datos:** Se integró `mypy` y `pandas-stubs` al flujo de trabajo. A pesar de la naturaleza dinámica de Pandas, el uso de stubs de tipos eleva la robustez de la capa de transformación y previene errores de "AttributeError" en tiempo de ejecución.

### 💡 Lecciones Aprendidas (Learnings)
- **Stubs de Pandas:** La instalación de `pandas-stubs` es crítica; sin ellos, `mypy` no puede validar las operaciones de DataFrame, dejando la capa de datos vulnerable a errores de tipado silenciosos.
- **Códigos de Error en el Contrato:** Vincular las excepciones directamente a los códigos `ERR_XX` del `contract.md` facilita la trazabilidad entre el fallo técnico y la especificación de negocio.

---

## [2026-04-26] - Certificación de Salud Estadística (Slice 1: Silver)

**Fase Actual:** Fase 2: Ingeniería y Modelado
**Contexto:** Ejecución de las tareas `T-2.1.1.DRIFT.RED` y `T-2.1.1.DRIFT.GRN` para la detección de deriva.

### ⚖️ Decisiones
1. **Detección de Deriva mediante Z-score:** Se implementó la lógica de Z-score (Desviación absoluta respecto a la media / Desviación estándar) para detectar cambios significativos en la distribución del batch. El umbral se fijó en `Z > 3` (3 sigmas), siguiendo el **Contrato de Datos**.
2. **Alertas No Bloqueantes (`Warning`):** Se decidió implementar `StatisticalDriftWarning` como una subclase de `Warning` en lugar de una excepción bloqueante. Esto cumple con el contrato donde la deriva genera alertas de telemetría (`ERR_06`) pero permite que el pipeline continúe la inferencia si los datos son biológicamente válidos.
3. **Inyección de Baseline Stats:** El método `check_drift` recibe un diccionario de estadísticas base. Esto permite que la validación sea dinámica y pueda ser alimentada desde el dataset de entrenamiento original o un repositorio de metadatos.

### 💡 Lecciones Aprendidas (Learnings)
- **Separación de Rangos y Distribución:** La validación biológica (`RangeValidationError`) es una regla de negocio (Hard Reject), mientras que la deriva estadística es una regla de salud del modelo (Soft Alert). Mantener esta separación es clave para la disponibilidad del sistema.

---

## [2026-04-26] - Validación de Contrato Rígido con Pydantic (Slice 1: Silver)

**Fase Actual:** Fase 2: Ingeniería y Modelado
**Contexto:** Ejecución de `T-2.1.1.VAL.RED` y `T-2.1.1.VAL.GRN`.

### ⚖️ Decisiones
1. **Adopción de Pydantic v2 para Validación de Runtime:** Se seleccionó Pydantic como motor de validación por su alta performance y soporte para tipado estricto. Se configuró `ConfigDict(extra='forbid', strict=True)` para cumplir con la política de "No Extra Fields" y "No Coercion" del Contrato de Datos.
2. **Validación Lógica Cruzada (`@model_validator`):** Se implementaron validaciones biológicas complejas (ej: ancho < largo) que no son posibles con tipos simples. Esto asegura que el sistema rechace datos morfológicamente imposibles antes de que lleguen al modelo.
3. **Mapeo de ValidationError a Dominio:** Se decidió capturar el `ValidationError` de Pydantic y re-lanzar excepciones personalizadas (`RangeValidationError`, `SchemaValidationError`). Esto mantiene la interfaz de errores limpia y alineada con los códigos `ERR_01` a `ERR_07`.

### 💡 Lecciones Aprendidas (Learnings)
- **Strict Mode de Pydantic:** El flag `strict=True` es fundamental para evitar que Pydantic convierta strings a floats automáticamente, garantizando que el cliente de la API envíe el tipo de dato correcto.
- **TDD en el Contrato:** Definir el test RED con todas las violaciones posibles (nulos, rangos, lógica, extras, tipos) permitió construir un validador robusto en un solo paso iterativo.

---

## [2026-04-27] - Industrialización de la Inteligencia (Slice 2: Modelado)

**Fase Actual:** Fase 2: Ingeniería y Modelado
**Contexto:** Ejecución del Slice 2 completo de la Bala Trazadora, desde la definición de esquemas hasta la industrialización del motor de inferencia.

### ⚖️ Decisiones
1. **Adopción de LogisticRegression como Baseline:** Se seleccionó un modelo lineal estandarizado dada la separabilidad del dataset Iris. Logró un rendimiento del 100% (Accuracy/F1), cumpliendo con creces los umbrales del BRD sin necesidad de arquitecturas complejas (Simplicity First).
2. **Implementación del "Virginica Shield" en el Motor:** Se decidió inyectar la lógica de seguridad directamente en el método predict del InferenceEngine. Esto garantiza que cualquier predicción de la clase Virginica con confianza inferior al 98% (umbral de penalización crítica) sea marcada para revisión manual (
eeds_review=True), protegiendo al negocio de falsos positivos de alto costo.
3. **Mecanismo de Auditoría Aleatoria (Random QC):** Se implementó un trigger probabilístico (5%) que fuerza el estado 
eeds_review=True independientemente de la confianza del modelo. Esto permite recolectar un set de datos de control "ciego" para medir el rendimiento real en producción.
4. **Persistencia Dual (MLflow + Local):** Se decidió mantener el tracking en MLflow para el linaje del experimento, pero serializar también un artefacto local latest_model.pkl para facilitar la portabilidad de la Bala Trazadora en contenedores Docker.

### 💡 Lecciones Aprendidas (Learnings)
- **El Modelo no es suficiente:** La "inteligencia" del sistema reside más en la lógica de *Shielding* y gobernanza que en el algoritmo de ML en sí mismo. Un modelo perfecto puede fallar en producción si no tiene protecciones contra casos de borde o deriva.
- **TDD en Modelado:** Implementar primero los tests de negocio (	est_business_acceptance.py) y de interfaz (	est_prediction_interface.py) permitió que el entrenamiento del modelo fuera una tarea de "pasa/no pasa" objetiva, eliminando la ambigüedad del rendimiento.
