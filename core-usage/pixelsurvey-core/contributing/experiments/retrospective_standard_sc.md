# 🔬 Retrospective: Adding the "Standard Stated Choice" Experiment

This document provides a detailed technical analysis of the process of integrating the `standard_stated_choice` experiment type. It covers the implementation steps, the bugs encountered, and lessons learned for future contributors.

---

## 🎯 The Objective
Create a variation of the Stated Choice experiment that:
1.  Displays alternatives in a **tabular format** (Attributes as rows, Alternatives as columns).
2.  Supports a variable number of alternatives (2 to 5).
3.  Does not use images (Standard attributes only).
4.  Integrates selection radio buttons in the last row of the table.

---

## 🛠️ Step-by-Step Implementation

### 1. Data Parsing (The "Intelligence")
- **Action:** Created `StandardSCExperimentParser` inheriting from `SCExperimentParser`.
- **Why:** Since the data structure (attributes, alternatives, CSV format) is identical to a normal Stated Choice, inheritance allowed us to reuse all the logic for calculating database columns and variable names.

### 2. UI Generation (The "Body")
- **Action:** Created `generators/elements/experiments/standard_stated_choice/`.
- **Card Generator:** Reorganized the data to be "tabular-friendly" (grouping variables by attribute rather than by alternative).
- **Template:** Used Jinja2 loops to dynamically generate table headers and columns based on `n_alternatives`.

### 3. Registry (The "Activation")
- **Action:** Added the new classes to `EXPERIMENT_REGISTRY` in `survey_gen.py`.

---

## 🐞 Post-Mortem: Analysis of Errors

Durante la implementación, nos encontramos con dos errores críticos. Analizarlos es fundamental para que el sistema sea más robusto en el futuro.

### Error 1: `UnboundLocalError: fgen`
*   **Síntoma:** El generador fallaba al intentar poblar la base de datos con tareas aleatorias.
*   **Causa:** El archivo `database_gen.py` tiene un bloque `if/elif` que decide qué "Generador de Archivos" usar. Al ser un tipo nuevo, el sistema no sabía cuál elegir y la variable `fgen` quedaba sin definir.
*   **Riesgo Sistemático:** **Alto.** Actualmente, añadir un experimento requiere tocar **cuatro** registros diferentes:
    1.  `survey_gen.py` (Registro principal).
    2.  `parsers/experiment_parser.py` (Fábrica de Parsers).
    3.  `generators/database/database_gen.py` (Lógica de DB).
    4.  El propio `files_gen.py` del experimento.
*   **Lección:** Para el futuro, deberíamos centralizar el registro de experimentos en un solo lugar que maneje el Parser, el Card y el File Generator a la vez.

### Error 2: `TemplateNotFound: experiment_base.py.jinja`
*   **Síntoma:** El generador fallaba al renderizar la página.
*   **Causa:** Cálculo incorrecto de la ruta en `card_gen.py`. El código buscaba en `generators/elements/pages` en lugar de `generators/pages`.
*   **Riesgo Sistemático:** **Medio.** Las estructuras de carpetas profundas hacen que encadenar `os.path.dirname` sea frágil.
*   **Lección:** Es mejor usar rutas absolutas relativas a la raíz del proyecto o una clase de utilidad para rutas.

---

## 📝 Recomendaciones Actualizadas para Contribuidores

Basado en esta experiencia, hemos actualizado los consejos para futuros desarrolladores:

1.  **La Triple Verificación del Registro:** Asegúrate de que el nuevo tipo esté en `survey_gen.py`, `experiment_parser.py` Y `database_gen.py`.
2.  **Cuidado con los Niveles de Carpeta:** Si tu experimento está muy profundo (ej: `standard_stated_choice`), necesitas subir **3 niveles** para llegar a la carpeta raíz de `generators/` y encontrar las plantillas base.
3.  **Tablas Dinámicas:** Usa siempre bucles de Jinja2 (`range`, `loop.index`) para que tu tabla soporte desde 2 hasta 5 alternativas sin romperse.

---

## ✅ Resultado Final
El `standard_stated_choice` no es solo un nuevo tipo de experimento; es ahora el **blueprint** (plano) perfecto para cualquier experimento tabular futuro en PixelSurvey.
