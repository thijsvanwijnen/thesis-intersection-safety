# 📝 Contributing New Question Types

This guide explains how to extend PixelSurvey with new question types. By following this pattern, you ensure that your contribution is modular and easy to maintain.

---

## 🏗️ The 4-Step Contribution Workflow

To add a new question type, you need to create or modify 4 things:

### 1. The YAML Definition
Define how the user will configure the question in their `survey.yaml`.
- Choose a unique `type` name (e.g., `likert_scale`, `rating_star`).
- Decide which parameters are needed (e.g., `options`, `scale_max`).

📄 **See Example:** [likert_scale.yaml](examples/likert_scale.yaml)

### 2. The Visual Template (`.py.jinja`)
Create a Jinja2 template file in `generators/elements/questionnaire/questions/`.
- Use standard Dash and Dash Bootstrap Components.
- **Rule:** You MUST include a hidden component with the ID `question-{{ question_id }}`. This is the source of truth for the database.
- Use `{{ variable }}` to inject values from the YAML data.

📄 **See Example:** [likert_scale.py.jinja](examples/likert_scale.py.jinja)

### 3. The Generator Class (`_gen.py`)
Create a Python class in `generators/elements/questionnaire/questions/` that handles the rendering.
- **`generate()`**: Loads the `.jinja` template and returns the rendered string.
- **`generate_callbacks()`**: (Optional) Returns a string containing the Dash `@callback` code. This is essential if your question has multiple inputs that need to be combined into one.

📄 **See Example:** [likert_scale_gen.py](examples/likert_scale_gen.py)

### 4. The Registry
Register your new class in `generators/elements/questionnaire/questionnaire_gen.py`.
- Import your generator class.
- Add a mapping to the `QUESTION_REGISTRY` dictionary.

📄 **See Example:** [registry_entry.py](examples/registry_entry.py)

---

## 🧪 Best Practices

1.  **Response Aggregation**: If your UI has multiple inputs (like a table of radio buttons), use a Dash callback to join them with a `/` separator and store the result in the hidden `question-{id}` input.
2.  **Naming Consistency**:
    -   Class: `YourTypeNameCard`
    -   File: `your_type_name_gen.py`
    -   Template: `your_type_name.py.jinja`
3.  **Imports**: The generated activity pages already import `dash`, `dcc`, `html`, `callback`, `Input`, `Output`, `State`, and `dbc`. You can use these freely in your templates and callbacks.

---

## 🚀 Next Steps
Once you've implemented these steps, run the survey generator to verify that your new question type appears correctly in the generated Dash app.
