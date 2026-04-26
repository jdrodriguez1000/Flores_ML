---
name: backlog-orchestration
description: Protocolo para la gestión jerárquica del proyecto, atomización de especificaciones técnicas y aseguramiento del DoD.
user-invocable: false
agent: ai-backlog-manager
allowed-tools: [Read, Write, Edit, Bash]
---

# Skill: Orquestación de Backlog

Esta habilidad permite transformar el plan maestro en acciones ejecutables, asegurando la trazabilidad total del proyecto.

## Funciones

### 1. Inicialización de Roadmap (Slices Verticales)
**Acción:** `initialize_roadmap`
- Crea el archivo `docs/governance/backlog.md`.
- Estructura el Backlog usando un enfoque iterativo de **Slices Verticales (Balas Trazadoras)** en lugar de cascada:
    - **Iteración 0 (Discovery):** Generación de la línea base documental (BRD, SAD, SpecDD, BDD).
    - **Iteración 1 (Tracer Bullet):** Selección de **UN solo** escenario BDD o variable clave. Ejecución transversal (Data Engineering -> Modeling -> UI Delivery) para esta única variable hasta validarla E2E.
    - **Iteraciones 2..N (Expansión):** Adición iterativa de nuevos escenarios BDD, completando el ciclo RED/GREEN transversal por cada uno.
- **Prohibición de Cascada:** El Backlog NUNCA debe estructurarse exigiendo terminar el 100% de la capa de datos antes del modelo, ni el 100% del modelo antes del frontend.

### 2. Atomización de SpecDD (TDD Mapping)
**Acción:** `atomize_specs_to_tasks`
- Escanea el `SpecDD`, el `Data Contract` y, obligatoriamente, el `docs/governance/behavior.md` (BDD).
- **Regla Mandatoria RED/GREEN:** Por cada componente definido, genera obligatoriamente dos ítems vinculados en el Backlog, **anclados a un escenario BDD**:
    1.  **Tarea [RED]:** Desarrollo de la Suite de Pruebas. El DoD es el fallo controlado del test asociado al escenario BDD.
    2.  **Tarea [GREEN]:** Implementación de la lógica productiva. El DoD es que el test asociado pase exitosamente a `GREEN`.
- Asigna el agente responsable (ej: `ai-data-engineer` para la lógica y `ai-data-sdet` para el test).

### 3. Gestión de Tareas (Task Management)
**Acción:** `manage_task_state`
- Actualiza el estado de las tareas (Block, In Progress, Done).
- Verifica el **DoD (Definition of Done)** antes de marcar como finalizada.
- Asegura que el responsable sea único por tarea.

## Estructura de Tarea en backlog.md
```markdown
### [ID] Título de la Tarea
- **Responsable:** @agente-nombre
- **Iteración:** X.Y
- **Entregable:** Nombre del Archivo/Componente
- **Acción:** [Coding | Testing | Documentation]
- **BDD Target:** [ID del Escenario en behavior.md]
- **DoD:** Tests E2E/Unitarios para el escenario target arrojan GREEN.
- **Estado:** [TODO | IN_PROGRESS | DONE]
```

## Reglas de Validación
- **Prohibido la multifunción:** Si una tarea dice "Desarrollar y Probar", debe ser rechazada y separada en dos tareas independientes.
- **Trazabilidad Absoluta al BDD:** Toda tarea técnica debe citar el escenario exacto del `behavior.md` (BDD). Si una tarea no puede ser mapeada a un escenario BDD, debe ser devuelta al Estratega de Negocios por representar comportamiento no documentado ni acordado.


---

## 🛡️ Mandatos de Gobernanza Global (Alineación process.md)
1. **BDD-as-DoD Absoluto:** Tu tarea no está terminada (DONE) ni lista para revisión humana hasta que el test automatizado asociado al escenario BDD arroje `GREEN`.
2. **Context Isolation:** Opera estrictamente bajo la regla de "Necesidad de Saber". Reclama solo tu archivo objetivo, tu prueba y tu fragmento del SpecDD. Rechaza contextos globales masivos.
3. **Tracer Bullets (Slices Verticales):** Ejecuta tu trabajo de manera iterativa por variable o funcionalidad específica (end-to-end). Está prohibido el desarrollo horizontal masivo.
