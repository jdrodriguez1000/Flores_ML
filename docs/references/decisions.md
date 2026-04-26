# Registro de Decisiones y Lecciones Aprendidas - Flores_ML

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
