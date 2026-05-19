# 🚀 Contributing to PixelSurvey Core

Welcome to the PixelSurvey contribution guide! We are excited to have you here.

To keep the project organized and easy to extend, we have separated our contribution guides based on what you want to add:

## 📁 Contribution Guides

### 1. 📝 [Adding New Question Types](contributing/questions/README.md)
Learn how to add new elements to questionnaires (e.g., Likert scales, Star ratings, etc.). This guide uses a modular architecture with Jinja2 templates and a Registry Pattern.

### 2. 🔬 [Adding New Experiment Types](contributing/experiments/README.md)
*(Coming Soon)* Learn how to create new interactive experimental paradigms like Stated Choice or Similarity Judgment.

---

## 🛠️ General Workflow

1.  **Fork** the repository.
2.  Create a new branch for your feature: `git checkout -b feature/your-feature-name`.
3.  Implement your changes in the **`development`** branch.
4.  Test your changes by generating a sample survey.
5.  Submit a **Pull Request** to the `development` branch of the main repository.

## ⚖️ Code Standards

-   Use **Jinja2 templates** for UI elements.
-   Follow the **Registry Pattern** for easy integration.
-   Maintain clear separation between visual design and generation logic.
-   Keep response formats consistent (e.g., using `/` as a separator for multi-input questions).

---

Thank you for contributing to the future of academic research tools! 🎊
