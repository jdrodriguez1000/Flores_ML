# Registro de Decisiones y Lecciones Aprendidas - Flores_ML

---

## [2026-04-26] - Blindaje Metodológico Nivel 3: TDD y Automatización Absoluta del Backlog

**Fase Actual:** Fase 2: Ingeniería y Modelado (Preparación)
**Contexto:** Auditoría profunda del `backlog.md` para la Iteración 2.1 bajo el rigor de "Abogado del Diablo" y principios MLOps avanzados.

### ⚖️ Decisiones
1. **Blindaje TDD Nivel 3 del Backlog:** Se rechazó cualquier validación manual o reporte visual como criterio de éxito (DoD). Se mandató que el 100% de los entregables técnicos y de negocio estén precedidos por una aserción automatizada (RED).
2. **Automatización de la Salud Estadística:** Se sustituyó el reporte EDA manual por un test de Deriva Distribucional (`DRIFT.RED`) integrado en el pipeline, garantizando que la calidad del dato sea una constante técnica y no un juicio subjetivo.
3. **TDD Verdadero en Infraestructura y Docker:** Se invirtió el orden de construcción de contenedores. Ahora es obligatorio escribir el test de salud del servicio (`SMK.RED`) antes de construir la imagen Docker (`DOCK.GRN`), evitando "falsos positivos" de despliegue donde el contenedor corre pero el servicio falla.
4. **Separación de Performance y Observabilidad:** Se dividió el refactor de la API en dos tareas atómicas: Optimización de Latencia (`PERF`) y Formato de Logs JSON (`OBS`). Esto asegura que el cumplimiento de los SLAs de velocidad no oculte fallos en la trazabilidad del sistema.
5. **Desacople de Gobernanza de Datos:** Se separó la Ingesta física (`A.GRN`) del Registro de Linaje (`LIN.GRN`). Esto garantiza que fallos en la capa de metadatos no bloqueen el flujo de carga de datos, manteniendo la trazabilidad atómica y aislada.
6. **Certificación E2E sin Intervención Humana:** Se eliminó el "UAT visual" como hito técnico. El cierre de la UI ahora depende exclusivamente de una suite E2E (Selenium/Playwright) al 100% en verde, alineándose con el mandato global de **BDD-as-DoD**.

### 💡 Lecciones Aprendidas (Learnings)
- **El UAT manual es Deuda Técnica:** Confiar en la verificación ocular al final de una iteración es un riesgo inaceptable en sistemas de IA. La suite de pruebas E2E debe ser el único juez de la integridad de la experiencia de usuario.
- **La Infraestructura también es Código:** Los servicios de soporte (MLflow, DBs) deben ser validados mediante tests de conectividad automáticos (`RED`) antes de iniciar procesos costosos como el entrenamiento, eliminando tiempos muertos de depuración.
- **Atomicidad = Diagnóstico Veloz:** Al separar el linaje de la ingesta, un error en la base de datos de metadatos no detiene el pipeline de datos, permitiendo una recuperación parcial y un aislamiento claro de la falla.

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
... (Rest of history preserved)
