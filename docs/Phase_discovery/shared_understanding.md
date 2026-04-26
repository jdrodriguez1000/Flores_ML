# Shared Understanding Log - Flores_ML

Este documento registra el proceso de descubrimiento y los acuerdos alcanzados durante la Fase 0 para garantizar que todos los agentes y stakeholders tengan una visión unificada del proyecto.

---

## Sesión de Descubrimiento (26 de abril de 2026)

### 1. Problema de Negocio y Usuarios
**Pregunta:** ¿Cuál es el problema de negocio específico que el sistema de clasificación "Flores_ML" busca resolver y quiénes serán los usuarios finales de estas predicciones?
**Respuesta:** Actualmente los analistas que clasifican las flores lo realizan de forma manual. Aunque tienen experiencia, no siempre entregan los mejores resultados, lo cual genera dudas y reprocesos porque otro analista debe validar o repetir la clasificación.
**Implicación para IA:** El sistema debe actuar como un validador de alta precisión para reducir la variabilidad inter-analista y eliminar la necesidad de dobles chequeos.

### 2. Indicadores Clave de Éxito (KPIs)
**Pregunta:** ¿Cuál sería el indicador clave de éxito (KPI) para este proyecto? ¿Qué porcentaje de reducción de reprocesos o qué nivel de precisión (Accuracy) mínima debe alcanzar el modelo para que el negocio confíe en él?
**Respuesta:** Reducir la tasa de reprocesos en un 80% y lograr un Accuracy superior al 96%.
**Implicación para IA:** El modelo no solo debe ser preciso, sino que debemos implementar una métrica de "Score de Confianza". Si el modelo tiene dudas (confianza < X%), debe derivar a un analista, pero en el 96% de los casos debe ser autónomo y certero.

### 3. Costo del Error y Penalización
**Pregunta:** ¿Hay algún tipo de error que sea más costoso para el negocio? ¿Existen especies de "alto valor" donde el error deba ser penalizado con mayor rigor?
**Respuesta:** Confundir una especie de alto valor comercial (o protegida) con una común es el error más costoso. Se debe priorizar la confianza para evitar el reproceso de registros críticos.
**Implicación para IA:** Se explorará el uso de matrices de costo durante el entrenamiento para penalizar desproporcionadamente las clasificaciones erróneas en especies sensibles.

### 4. Origen y Calidad de los Datos
**Pregunta:** ¿Cuál es la fuente de los datos para el entrenamiento y qué volumen de registros tenemos disponibles aproximadamente?
**Respuesta:** Dataset Iris (Robert Fisher), ubicado en `data/Bronze/Iris.csv`. Son 150 registros ya etiquetados y validados por expertos.
**Implicación para IA:** La base es sólida (Ground Truth de alta calidad), pero el volumen es bajo (150 registros), lo que exige modelos con alta capacidad de generalización y validación cruzada (Cross-Validation) rigurosa para evitar el sobreajuste.

### 5. Interfaz y Flujo de Trabajo (UX)
**Pregunta:** ¿Cómo interactuarán los analistas con el sistema en su día a día?
**Respuesta:** A través de un Dashboard web donde ingresarán los 4 valores morfológicos. El sistema devolverá la clasificación y un nivel de confianza.
**Implicación para IA/Dev:** El backend debe ser capaz de procesar la inferencia y calcular la probabilidad de la clase (confianza) en tiempo real para ser mostrada en el frontend.

### 6. Restricciones Técnicas
**Pregunta:** ¿Existe alguna restricción de latencia o conectividad?
**Respuesta:** Latencia de hasta 2-3 segundos es aceptable. El sistema será online (web-based) y accesible desde las estaciones de trabajo de los analistas.
**Implicación para IA/Dev:** No se requiere optimización extrema de latencia, lo que permite el uso de modelos más robustos (aunque sean ligeramente más pesados) para maximizar el Accuracy.

### 7. Mapeo de Valor y Penalización
**Pregunta:** Dado que usaremos el dataset Iris, ¿cuál de las tres especies (Setosa, Versicolor, Virginica) consideraremos como la de "alto valor comercial" para penalizar sus errores?
**Respuesta:** La especie **Virginica** será considerada la de "alto valor".
**Implicación para IA:** Se implementará una penalización asimétrica (matriz de costos) en la función de pérdida del modelo o en el umbral de decisión, donde clasificar erróneamente una Virginica o como Virginica, tenga un impacto negativo mayor.

### 8. Umbral de Confianza Operativo
**Pregunta:** ¿Qué umbral mínimo de confianza (porcentaje) definiremos para que el sistema emita la clasificación de forma automática sin enviar la alerta de revisión manual?
**Respuesta:** Se establece un umbral de confianza del **85%**. Predicciones con confianza $\ge$ 85% se aceptan automáticamente; si es menor a 85%, el sistema muestra una alerta visual en el dashboard para que el analista lo revise manualmente.
**Implicación para IA:** El modelo debe estar perfectamente calibrado para que las probabilidades devueltas sean fiables. Se usará *Probability Calibration* post-entrenamiento si es necesario.

### 9. Línea Base y Medición de Impacto
**Pregunta:** Aproximadamente, ¿cuántas clasificaciones manuales se realizan al mes actualmente y qué porcentaje terminan en reproceso?
**Respuesta:** Actualmente se realizan ~1,000 clasificaciones mensuales, con un 15% (150 registros) que requieren reproceso. El objetivo del 80% de reducción significa bajar a un máximo de **30 reprocesos mensuales**.
**Implicación para IA:** Este dato convierte el "85% de confianza" en un requerimiento duro: el modelo no debe generar alertas de baja confianza en más del 3% de los casos totales (30 de 1000) si queremos cumplir con el caso de negocio al 100%.

### 10. Validación de Entrada (Data Contract)
**Pregunta:** ¿Qué acción debe tomar el sistema si el usuario ingresa valores inválidos (negativos o gigantes) por error en el dashboard?
**Respuesta:** El sistema aplicará validación estricta desde el frontend y la API. Si los valores están fuera del rango biológicamente posible para las flores (ej. > 0 cm y < 15 cm), se rechazará la predicción con un error claro.
**Implicación para IA:** Se establecerá un contrato de datos estricto (`Null Policy` y reglas de rango) antes de que la inferencia ocurra, protegiendo al modelo de datos "Out of Distribution" (Garbage In = Garbage Out).

### 11. Estrategia de Contingencia frente al Data Drift
**Pregunta:** Entrenaremos con solo 150 registros pero procesaremos 1,000 casos nuevos al mes. Existe un alto riesgo de 'Data Drift' (cambios en la distribución), lo que podría causar que el modelo baje su confianza (< 85%) y envíe a revisión manual mucho más del límite de 30 casos al mes, incumpliendo el KPI. ¿Cuál es la estrategia operativa si la tasa de revisión manual se dispara por encima de nuestro límite tolerable?
**Respuesta:** Implementar un **Feedback Loop Activo (Human-in-the-loop)**. Los casos enviados a revisión manual serán re-etiquetados por los analistas expertos. Estas nuevas muestras corregidas se agregarán al conjunto de datos histórico para programar **reentrenamientos periódicos** del modelo, permitiendo que la IA se adapte a las nuevas distribuciones de datos y mantenga el KPI bajo control.
**Implicación para IA/Dev:** El sistema debe contar con un mecanismo de captura de retroalimentación (Feedback Capture) en el backend donde la clasificación final dictada por el analista quede registrada en una base de datos para el futuro reentrenamiento del pipeline de MLOps.

### 12. Retorno de Inversión (ROI) y Costo de Oportunidad
**Pregunta:** Implementar esta solución generará costos de infraestructura en la nube y mantenimiento. ¿Tenemos una estimación del costo actual de los 150 reprocesos mensuales? Debemos asegurar que el Costo Total de Propiedad (TCO) del sistema sea menor que el costo del proceso manual actual.
**Respuesta:** Aunque el negocio no tiene el costo exacto medido en dinero, el mayor impacto es la **pérdida de credibilidad** ante los clientes. Adicionalmente, cada reproceso requiere reunir a los analistas y toma entre **60 y 90 minutos** para llegar a un consenso.
**Implicación para IA/Negocio:** Esto justifica plenamente el caso de negocio. 150 reprocesos a ~75 minutos promedio equivalen a casi **187 horas mensuales** de tiempo experto perdido, lo cual es inmensamente superior al costo operativo de una API para el modelo. La reducción de tiempos de respuesta a los clientes y la mejora en la reputación garantizan un ROI altamente positivo.

### 13. Estrategia de Lanzamiento y Mitigación de Riesgos (Dashboard)
**Pregunta:** Entrenaremos con 150 registros pero procesaremos 1,000 mensuales. Hay un alto riesgo de que los datos no representen la variabilidad actual. ¿Cómo mitigaremos el riesgo en producción inicial sin retrasar el despliegue del Dashboard?
**Respuesta:** El Dashboard Web se desplegará desde el Día 1, pero la IA operará bajo un **"Shadow Mode" (Modo Sombra)** oculto mediante un Feature Flag. 
**Implicación para IA/Dev/Negocio:** 
* **Fase 1 (Silenciosa):** Los analistas usarán el nuevo dashboard para ingresar datos y su clasificación manual. El backend ejecutará la IA y guardará su predicción + confianza silenciosamente en la base de datos para comparar (Ground Truth vs Predicción) sin sesgar al usuario ni arriesgar credibilidad.
* **Fase 2 (Activa):** Una vez que auditoría confirme un *Accuracy real > 96%* en producción, se activará el Feature Flag. El dashboard comenzará a mostrar las predicciones de la IA y aplicará la regla de auto-aprobación (Confianza $\ge$ 85%) o alerta de revisión manual.

### 14. Matriz de Costos para Virginica
**Pregunta:** Siendo 'Virginica' la especie de alto valor, ¿cuál error es más grave: el falso positivo o el falso negativo?
**Respuesta:** Ambos errores se consideran críticamente inaceptables (Penalización Simétrica).
**Implicación para IA:** La función de pérdida (Loss Function) del modelo incluirá pesos que penalicen de manera severa y simétrica cualquier clasificación errónea que asigne la etiqueta Virginica a otra especie, o viceversa, obligando al modelo a aislar esta clase con el máximo rigor posible.

---
