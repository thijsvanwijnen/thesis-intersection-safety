from pathlib import Path

# Get the project root directory (parent of pixelsurveygen)
PROJECT_ROOT = Path(__file__).parent.parent  # Goes up from vars.py to project root
PROGRAM_DIR = Path(__file__).parent

# Input/Output directories (relative to project root)
RECIPES_DIR = PROJECT_ROOT / "recipes"
SURVEYS_DIR = PROJECT_ROOT / "surveys"

# Generator-related paths
GENERATORS_DIR = PROGRAM_DIR / "generators"
PAGES_GEN_DIR = GENERATORS_DIR / "pages"
DATABASE_GEN_DIR = GENERATORS_DIR / "database"

# Templates
DATABASE_TEMPLATE = DATABASE_GEN_DIR / "database_template.txt"
APP_TEMPLATE = PAGES_GEN_DIR / "app_template.txt"
HOME_TEMPLATE = PAGES_GEN_DIR / "home_template.txt"
CONSENT_TEMPLATE = PAGES_GEN_DIR / "consent_template.txt"
SCREENING_TEMPLATE = PAGES_GEN_DIR / "screening_template.txt"
INSTRUCTIONS_TEMPLATE = PAGES_GEN_DIR / "instructions_template.txt"
EXPERIMENT_TEMPLATE = PAGES_GEN_DIR / "experiment_template.txt"
QUESTIONNAIRE_TEMPLATE = PAGES_GEN_DIR / "questionnaire_template.txt"
END_TEMPLATE = PAGES_GEN_DIR / "end_template.txt"
FULLQUOTA_TEMPLATE = PAGES_GEN_DIR / "fullquota_template.txt"

# Source resources paths
SOURCE_DIR = PROGRAM_DIR / "source"
PIXELSURVEY_LOGO = SOURCE_DIR / "logo" / "pixelsurvey.png"