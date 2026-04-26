# Data Contract - Flores_ML

## 1. Introducción
Este contrato de datos define los estándares técnicos, validaciones y reglas de transformación obligatorias. Es la ley para el `DataProcessor` y el `AuditRepository`. Cualquier desviación de este contrato disparará un rechazo inmediato del set de datos o de la petición API.

### 1.1. Clasificación de Seguridad y Sensibilidad (PII)
- **Nivel de Confidencialidad:** Público (Nivel 0).
- **PII (Personal Identifiable Information):** Ninguna. El dataset contiene exclusivamente mediciones morfológicas botánicas. No se requiere cifrado en reposo para los pipelines de datos.
- **Audit Logs:** El campo `analyst_id` en el Feedback Loop se considera dato de uso interno; no requiere enmascaramiento, pero el acceso al repositorio de auditoría debe ser restringido.

---

## 2. Mapeo y Normalización (Bronze → Silver)
Para asegurar el cumplimiento del **Leakage Shield**, se establece el siguiente mapeo obligatorio. **Unidad de Medida base: Centímetros (cm).**

| Columna Original (Bronze) | Campo Normalizado (Silver/API) | Acción | Unidad |
| :--- | :--- | :--- | :--- |
| `Id` | - | **DESCARTAR (Leakage Shield)** | - |
| `SepalLengthCm` | `sepal_length` | Rename + Cast (float64) | cm |
| `SepalWidthCm` | `sepal_width` | Rename + Cast (float64) | cm |
| `PetalLengthCm` | `petal_length` | Rename + Cast (float64) | cm |
| `PetalWidthCm` | `petal_width` | Rename + Cast (float64) | cm |
| `Species` | `species` | Rename + Cast (SpeciesEnum) | - |

### 2.1. Normalización de Target (SpeciesEnum)
Las etiquetas deben normalizarse al siguiente Enum estricto (Case-Sensitive):
- `Setosa`
- `Versicolor`
- `Virginica`

---

## 3. Políticas de Calidad y Validación

### 3.1. Null Policy (Hard Reject)
No se permite imputación. Cualquier valor `null` o `NaN` en las 4 características morfológicas dispara un error `ERR_04 (NullInputError)`.

### 3.2. Range Validation (Biological Constraints)
Los valores deben estar en el intervalo **[0.1, 15.0]**. Valores fuera disparan `ERR_01 (RangeValidationError)`.

### 3.3. Cross-Feature Validation (Logical Consistency)
Para garantizar integridad biológica, se aplican las siguientes reglas:
- **Petal Consistency:** `petal_width` DEBE ser menor que `petal_length`.
- **Sepal Consistency:** `sepal_width` DEBE ser menor que `sepal_length`.
El incumplimiento dispara `ERR_05 (LogicConsistencyError)`.

### 3.4. Duplicate Policy
- **Bronze -> Silver:** Se permite la existencia de registros idénticos si provienen de la fuente original. 
- **Silver -> Gold:** Se debe realizar un `drop_duplicates()` para evitar sobre-representación en el entrenamiento, manteniendo solo la primera ocurrencia.

### 3.5. Estabilidad Estadística (Drift Detection)
Para el monitoreo de producción, se establecen los siguientes umbrales de alerta:
- **Alert Trigger:** Si la media móvil de 100 registros se desvía más de **3 sigma (Z-score > 3)** respecto al dataset de entrenamiento original.
- **Acción:** Disparar `ERR_06 (StatisticalDriftWarning)` en logs/telemetría (no bloquea inferencia, pero requiere revisión).

### 3.6. Reglas de Decisión e Inferencia (Thresholds)
El campo `needs_review` en la respuesta de la API será `true` estricta y únicamente si se cumple alguna de las siguientes condiciones:
1. **Baja Confianza:** `confidence` es menor a `0.85` (CONFIDENCE_THRESHOLD).
2. **Virginica Shield:** La predicción es `Virginica` y la `confidence` es menor a `0.98` (VIRGINICA_THRESHOLD).
3. **Audit Randomizer:** El sistema selecciona el 5% (`0.05` AUDIT_RATE) de las predicciones aleatoriamente para auditoría de calidad.

### 3.7. Política de Frontera Estricta (Strict Payload & Security)
Para prevenir ataques de inyección y saturación:
- **No Extra Fields:** El servidor **RECHAZARÁ** (HTTP 422 - `ERR_07`) cualquier petición JSON que contenga llaves no definidas explícitamente en este contrato.
- **Tipado Estricto (No Coercion):** No se permite la coerción de tipos (ej. enviar `"5.1"` como string en lugar del float `5.1`).

### 3.8. Persistencia Física y Tipado en Disco (Storage Contract)
Para garantizar que el tipado estricto (Enums, float64) no se degrade entre fases:
- **Prohibido el uso de CSV/JSON** para las capas `Silver` y `Gold`.
- Todo dataset procesado DEBE persistirse exclusivamente en formato columnar **Parquet (compresión Snappy)**, embebiendo el esquema de datos directamente en el archivo.

### 3.9. Política de Tiempo (UTC-Only)
Para evitar corrupciones en el linaje y logs de auditoría:
- Todo `timestamp` generado por el sistema (predicciones, metadata, feedback) DEBE estar en zona horaria **UTC estricta** (Formato ISO-8601 con sufijo `Z`, ej: `2026-04-26T12:00:00Z`). Servidores locales no deben inyectar su huso horario.

### 3.10. Política de Reentrenamiento (Feedback Override)
Para el ciclo cerrado (Closed-Loop), al generar la capa **Gold** a partir de **Silver**:
- **Sobrescritura:** Si existe un registro de corrección en el Repositorio de Auditoría, la etiqueta `manual_species` del experto **SOBREESCRIBE** la etiqueta original.
- **Descarte de Ruido:** Si el experto marcó `is_valid_sample` como `false` en el Feedback, ese registro se **ELIMINA** permanentemente de la capa Gold para no envenenar el reentrenamiento.

---

## 4. Esquemas de Intercambio (API Payload)

### 4.1. Request (Input) - Sincronizado con SpecDD
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

### 4.2. Response (Output) - Sincronizado con SpecDD
El payload de salida también está sujeto a validación estricta antes de ser emitido. Si el modelo interno produce un `confidence` < 0.0 o > 1.0, el sistema deberá fallar internamente y no emitir datos corruptos.
```json
{
  "prediction_id": "uuid-v4-generated-by-repo",
  "species": "Setosa",
  "confidence": 0.99,
  "needs_review": false,
  "model_version": "1.0.0",
  "prediction_timestamp": "2026-04-26T12:00:00Z",
  "execution_time_ms": 12.5,
  "shadow_mode": false
}
```

---

## 5. Esquema de Feedback Loop (Audit Payload)
Payload obligatorio para el endpoint `POST /api/v1/feedback`.

| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `prediction_id` | string (UUIDv4) | SÍ | ID retornado en la respuesta de inferencia. Debe validar formato estricto UUIDv4. |
| `manual_species` | SpeciesEnum | SÍ | Etiqueta corregida por el experto. Se ignora si la muestra es inválida. |
| `is_valid_sample` | boolean | SÍ | `true` si es una flor válida. `false` si es ruido/fraude a descartar del Gold. |
| `analyst_id` | string | SÍ | ID del usuario. Máximo 50 caracteres alfanuméricos o email. |

---

## 6. Registro de Errores (Error Registry)
| Código | Excepción | HTTP Status | Descripción |
| :--- | :--- | :--- | :--- |
| `ERR_01` | `RangeValidationError` | 400 | Valores fuera de 0.1 - 15.0 cm. |
| `ERR_02` | `ModelLoadError` | 503 | Fallo al cargar el archivo .pkl. |
| `ERR_03` | `AuditStorageError` | 500 | Fallo al escribir en el repositorio de auditoría. |
| `ERR_04` | `NullInputError` | 400 | Campos faltantes o nulos en la entrada. |
| `ERR_05` | `LogicConsistencyError` | 400 | Inconsistencia biológica (ej: ancho > largo). |
| `ERR_06` | `StatisticalDriftWarning` | 200 | Alerta de deriva estadística (Non-Blocking). |
| `ERR_07` | `SchemaValidationError` | 422 | Error de tipado estricto (ej: string en vez de float) o Enum inválido. |

---

## 7. Linaje y Trazabilidad de Datos

### 7.1. Esquema de Metadata (`gold_metadata.json`)
Para garantizar la integridad MLOps y evitar falsos positivos de deriva, el cálculo del hash (`data_version_hash`) **NO DEBE** realizarse sobre el archivo físico (debido al no-determinismo de la compresión Parquet/Snappy). El hash debe calcularse lógicamente (ej. aplicando SHA-256 a las filas de datos reales serializadas o a la firma del dataframe).

```json
{
  "data_version_hash": "sha256-hex-string-of-logical-data",
  "contract_version": "1.8.0",
  "source_records_count": 150,
  "gold_records_count": 147,
  "processing_pipeline": "src.data.transformation.DataProcessor.process_batch",
  "generation_timestamp": "ISO-8601",
  "author_agent": "ai-data-engineer"
}
```

---

## 8. Control de Versiones del Contrato
| Versión | Fecha | Cambios |
| :--- | :--- | :--- |
| 1.0.0 | 2026-04-26 | Definición inicial. |
| 1.1.0 | 2026-04-26 | Mapeo Bronze-Silver, esquema de Feedback e integración de UUID. |
| 1.2.0 | 2026-04-26 | Auditoría completa: Sincronización con SpecDD, validaciones cruzadas, política de duplicados y Error Registry. |
| 1.3.0 | 2026-04-26 | Resiliencia Industrial: Umbrales de drift, blindaje de unidades y esquema rígido de metadata. |
| 1.4.0 | 2026-04-26 | Auditoría Final: Clasificación de seguridad (PII), SchemaValidationError (ERR_07) y Reglas de Inferencia (Thresholds). |
| 1.5.0 | 2026-04-26 | Securización de Frontera: Política estricta (Extra.forbid), prevención de DoS (longitud máxima) y validación UUIDv4. |
| 1.6.0 | 2026-04-26 | Arquitectura de Almacenamiento: Exigencia de Parquet para Silver/Gold, Política estricta UTC-Only y Output Bounds. |
| 1.7.0 | 2026-04-26 | Arquitectura Closed-Loop: Nueva política de sobreescritura/descarte (Feedback Override) y flag `is_valid_sample`. |
| 1.8.0 | 2026-04-26 | Integridad MLOps: Política de Hashing Lógico Determinista y Sincronización estricta con SpecDD. |
