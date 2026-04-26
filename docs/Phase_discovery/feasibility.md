# Reporte de Factibilidad de Datos (Data Feasibility Report) - Flores_ML

## 1. Veredicto de Viabilidad
**Estado:** 🟡 **GO WITH RISKS (Amarillo)**
La calidad técnica es alta (10/10), pero la auditoría profunda revela riesgos críticos de **Target Leakage**, **Solapamiento de Clases** e **Inestabilidad de Métricas**. El cumplimiento de los KPIs de negocio (>96% Accuracy y >98% F1 Virginica) es estadísticamente frágil dado el tamaño de la muestra (150 registros) y la posible obsolescencia del linaje.

## 2. Inventario de Fuentes y Catalogación
| Fuente | Tipo | Formato | Ubicación | Volumetría | Calidad (1-10) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Iris Dataset** | Archivo Plano | CSV | `data/Bronze/Iris.csv` | 150 registros | 10/10* |

*\*Nota: Calidad técnica alta, pero con incertidumbre sobre la precisión de las etiquetas originales (Ground Truth) debido a la variabilidad inter-analista reportada por el negocio.*

## 3. Diagnóstico de Salud (EDQ)

### 3.1. Integridad y Validez
- **Nulos:** 0.0%. Cumple con la Null Policy.
- **Duplicados:** 0 registros.
- **Rangos:** 100% dentro de los límites biológicos (0.1 cm - 15.0 cm).

### 3.2. Auditoría Estadística Profunda (Devil's Advocate)
- **Target Leakage & Sesgo de Recolección:** Correlación de **0.94** entre `Id` y especie. Requiere eliminación obligatoria de la columna y barajado (shuffling) profundo.
- **Solapamiento Crítico:** Solapamiento de hasta el 96% en medidas de sépalo entre Versicolor y Virginica. El éxito del modelo depende de una frontera de decisión extremadamente delgada en las variables del pétalo.
- **Inestabilidad de Métricas (Muestra Pequeña):** Con solo 50 registros de Virginica, fallar en una sola predicción durante el test reduce el F1-Score por debajo del umbral del 98%. La métrica es estadísticamente volátil.
- **Riesgo de Ruido en Etiquetas:** Si los analistas que generaron este dataset cometieron errores (como indica el BRD), el modelo entrenará con "verdades" falsas, impidiendo alcanzar la precisión requerida.
- **Prior Drift (Desbalance):** El dataset está balanceado (50/50/50), pero el flujo real del laboratorio podría no estarlo. El modelo puede ser sensible a cambios en la frecuencia de las especies en producción.

## 4. Análisis de Brechas (Gap Analysis)

| Requerimiento (BRD) | Realidad del Dato | Brecha | Mitigación |
| :--- | :--- | :--- | :--- |
| **F1 Virginica > 98%** | Solapamiento y muestra pequeña. | Fragilidad estadística. | Bootstrap Resampling (1000 iter.) y Matriz de Costos. |
| **Accuracy > 96%** | Posible ruido en etiquetas. | Incertidumbre de Verdad. | Re-validación ciega del 20% del dataset por experto. |
| **Integridad Inferencia** | Columna `Id` presente. | **Target Leakage.** | Eliminación de `Id` y barajado determinista. |
| **Robustez Operativa** | Distribución balanceada. | Riesgo de Prior Drift. | Stress testing con inyección de pesos de clase. |
| **Contrato BDD** | Nombres crudos (`SepalLengthCm`, `Iris-setosa`). | Desalineación de API. | Normalización estricta de esquema en capa Silver. |

## 5. Plan de Acción y Mitigación (Recomendaciones)
1. **Sanitización Crítica y Normalización (Silver):** Eliminar columna `Id`, aplicar shuffling estratificado y estandarizar la nomenclatura para cumplir el contrato BDD (ej: `SepalLengthCm` $\rightarrow$ `sepal_length`, `Iris-setosa` $\rightarrow$ `Setosa`).
2. **Blindaje de Etiquetas:** Someter el 20% del dataset (30 registros) a una re-validación ciega por un tercer experto para confirmar el Ground Truth.
3. **Feature Engineering:** Generar ratios morfológicos (ej: `Petal_Ratio`) para mejorar la separación de clases solapadas.
4. **Validación Bootstrap:** Sustituir K-Fold simple por **Bootstrap Resampling** (1000 iteraciones) para obtener intervalos de confianza reales.
5. **Stress Testing:** Simular escenarios de producción desbalanceados mediante inyección de pesos para verificar la estabilidad del Accuracy.
6. **Shadow Mode:** Calibración final obligatoria con las primeras 100 muestras en vivo antes de la activación del modelo.

---
**Auditor:** @ai-data-auditor
**Fecha:** 26 de abril de 2026
**Certificación de Auditoría:** ⚠️ APROBADO CON RESERVAS ESTADÍSTICAS Y OPERATIVAS
