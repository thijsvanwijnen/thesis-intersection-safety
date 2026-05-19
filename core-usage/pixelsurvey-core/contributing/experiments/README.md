# 🔬 Contributing New Experiment Types

This guide explains how to add new experimental paradigms to PixelSurvey. Experiments are more complex than questions because they often involve:
- Multiple tasks per respondent.
- Experimental designs (random or custom).
- Complex interactive layouts.
- Specialized data parsing.

---

## 🏗️ The 5-Step Experiment Contribution Workflow

### 1. The YAML Definition
Define your experiment in the `body` section of `survey.yaml`.
- Use `type: experiment`.
- Choose a unique `experiment_type` name (e.g., `standard_stated_choice`).

📄 **See Example:** [standard_sc.yaml](examples/standard_sc.yaml)

### 2. The Activity Parser
Experiments need a parser to handle their specific settings and data columns.
- **Location:** `parsers/experiment_parsers/`
- **Action:** Create a new parser class (e.g., `StandardSCExperimentParser`) inheriting from `ExperimentParser` (or `SCExperimentParser` if it's a variation).
- **Register:** Add your parser to the factory in `parsers/experiment_parser.py`.

### 3. The Generator Files (`files_gen.py` and `card_gen.py`)
- **Location:** `generators/elements/experiments/your_type/`
- **`files_gen.py`**: Handles generating example CSVs and random designs.
- **`card_gen.py`**: Loads the Jinja2 template and prepares the data for rendering.

### 4. The Jinja2 Template (`template.py.jinja`)
Define the visual layout of your experiment task.
- **Location:** `generators/elements/experiments/your_type/template.py.jinja`
- **Extend:** Experiments should `{% extends "experiment_base.py.jinja" %}`.
- **Blocks:** Override blocks like `task_content_generator`, `selection_toggle_callback`, etc.

### 5. The Registry
Register your new Generator class in the `EXPERIMENT_REGISTRY` located in `survey_gen.py`.

---

## 💡 Pro Tips for Experiments

1.  **Tabular Layouts**: For experiments comparing multiple alternatives, use `dbc.Table` to create a clear comparison grid.
2.  **Dynamic Alternatives**: If your experiment allows a variable number of alternatives (e.g., 2 to 5), use Jinja2 loops (`{% for alt_n in range(1, n_alternatives + 1) %}`) to generate the columns.
3.  **Inheritance**: If your new experiment is a variation of an existing one, don't repeat yourself! Inherit from existing Parsers and Generators where possible.

---

## 🚀 Submission
Follow the same testing and PR process as described in the main [CONTRIBUTING.md](../../CONTRIBUTING.md).
