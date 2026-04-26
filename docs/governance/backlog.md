# Proyecto Flores_ML - Backlog Maestro

Este documento orquesta la ejecución del proyecto bajo las metodologías **SpecDD**, **BDD** y **TDD**. Sigue una estructura de **Slices Verticales** para garantizar la validación continua.

---

## Fase 1: Descubrimiento y Entendimiento del Negocio
**Objetivo:** Transformar la necesidad de negocio en una especificación técnica ejecutable y validar la factibilidad de los datos.

### Iteración 1.0: Fundamentos y Entendimiento Compartido
| ID | Tarea | Responsable | Estado | BDD Target | DoD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T-1.1** | Registro de Entendimiento Compartido (Ask-Me) | @ai-business-strategist | TODO | N/A | `docs/Phase_discovery/shared_understanding.md` validado. |
| **T-1.2** | Configuración del Proyecto (Config) | @config-manager | TODO | N/A | `docs/references/config.md` generado. |
| **T-1.3** | Documento de Requerimientos de Negocio (BRD) | @ai-business-strategist | TODO | N/A | `docs/governance/BRD.md` aprobado con KPIs. |
| **T-1.4** | Contrato de Comportamiento (BDD) | @ai-business-strategist | TODO | N/A | `docs/governance/behavior.md` con escenarios Gherkin. |
| **T-1.5** | Reporte de Factibilidad de Datos | @ai-data-auditor | TODO | N/A | `docs/Phase_discovery/feasibility.md` con diagnóstico y plan de mitigación. |
| **T-1.6** | Diseño de Mockup Visual (Prototipo) | @ai-ux-designer | TODO | N/A | `mockup/index.html` con diseño estático finalizado. |
| **T-1.7** | Ciclo de Aprobación UAT de Interfaz | @ai-ux-designer | TODO | N/A | `docs/Phase_discovery/mockup.md` vinculante aprobado por Stakeholder. |
| **T-1.8** | Documento de Arquitectura de Software (SAD) | @ai-solutions-architect | TODO | N/A | `docs/governance/SAD.md` con topología y stack (C4 Model). |
| **T-1.9** | Especificación de Interfaces (SpecDD) | @ai-solutions-architect | TODO | N/A | `docs/governance/SpecDD.md` con firmas de módulos .py. |
| **T-1.10** | Contrato de Datos (Esquema de Datos) | @ai-solutions-architect | TODO | N/A | `docs/governance/contract.md` con Null Policy y Transformation Rules. |

---

## Fase 2: Ingeniería y Modelado (Slices Verticales)

### Iteración 2.1: Bala Trazadora (Tracer Bullet)
**Objetivo:** Ejecutar un flujo E2E transversal para una sola variable crítica para validar la arquitectura profunda.

#### [Slice: Ingesta y Limpieza Base]
- **T-2.1.RED:** Crear Suite de Pruebas para Ingesta (Bronze/Silver).
- **T-2.1.GREEN:** Implementar lógica de ingesta y limpieza en `src/`.
- **T-2.1.EDA:** Reporte de EDA de Ingesta y Transformación.

#### [Slice: Modelo de Referencia (Baseline)]
- **T-2.2.RED:** Crear Suite de Pruebas de Rendimiento (F1/Accuracy).
- **T-2.2.GREEN:** Entrenar Modelo Dummy/Baseline y serializar en `models/`.
- **T-2.2.QA:** Certificación de robustez del modelo base.

#### [Slice: API e Interfaz (UI) Mínima]
- **T-2.3.RED:** Test E2E de integración (Frontend -> Backend -> Modelo).
- **T-2.3.GREEN:** Exponer modelo vía FastAPI y conectar con UI básica.

---

## Leyenda de Estados
- 🔴 **TODO:** Tarea pendiente.
- 🟡 **IN_PROGRESS:** En ejecución.
- 🟢 **DONE:** Tarea certificada y validada.
- ⚪ **BLOCKED:** Bloqueada por dependencia externa.
