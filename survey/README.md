# 🚀 PixelSurvey Usage Environment

Welcome to the **PixelSurvey Usage Environment**. This repository serves as your workspace to create, manage, and run surveys using the `pixelsurvey-core` engine. 

By keeping the core engine as a Git submodule, this structure ensures a clean separation between the survey generation engine and your specific research data (recipes and generated surveys).

---

## 📁 Repository Structure

```text
core-usage/
├── pixelsurvey-core/    # The main survey generation engine (Git submodule)
├── recipes/             # Directory for your YAML survey configurations
├── surveys/             # (Generated) Output directory for created Dash surveys
├── requirements.txt     # Python dependencies needed for the core engine
└── run.py               # Helper script to manage your surveys
```

---

## 🛠️ Initial Setup
Follow these steps to set up your environment for the first time:

### 1. Clone the repository
Make sure to include the `--recursive` flag to pull the `pixelsurvey-core` submodule along with this repository.

```bash
git clone --recursive https://github.com/PixelSurvey/core-usage.git
cd core-usage
```

### 2. Set up the Python Environment
We highly recommend using a virtual environment to avoid dependency conflicts.

```bash
# Create a virtual environment named .psenv
python -m venv .psenv

# Activate the virtual environment (macOS/Linux)
source .psenv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

---

## 🏗️ Generating a Survey

To generate a new Dash survey application from a YAML recipe, use the core generator.

> [!IMPORTANT]
> **Recipe Folder Structure:**
> Inside the `recipes/` directory, you must create a specific folder for each survey using the `recipe-<survey_name>` naming convention. All your YAML configurations (like `survey.yaml`) and assets go inside that folder.
> 
> **Example structure:**
> If the `<survey_name>` is `stated_preference_example`, the folder structure should be:
> `recipes/recipe-stated_preference_example/survey.yaml`
> 
> When running the generator, you must pass exactly that `<survey_name>` (in this case, `stated_preference_example`).

```bash
# Ensure your virtual environment is active
source .psenv/bin/activate

# Generate the survey
python -m pixelsurvey-core.survey_gen <survey_name>
```

**Example:**
```bash
python -m pixelsurvey-core.survey_gen stated_preference_example
```
*This will read from `recipes/recipe-stated_preference_example/` and generate a new Dash app inside the `surveys/survey-stated_preference_example/` directory.*

---

## 🛠️ Generating templates for your experimental activities

After you have created the Survey YAML recipe. You can generate the CSV templates (examples) you need to fill for your experiments (custom or random) based the attributes names you have filled.

### 📄 Template files 

```bash
# Generate example templates in your recipe folder
python -m pixelsurvey-core.expirement_templates_gen <survey_name>
```
After running this command, a new folder `templates` will be added in your recipe folder with the templated ready to be filled with your edxperimental design data.


## ▶️ Running a Generated Survey (Debug Mode)

Once your survey is generated, you can run it locally to test the flow and verify the design before deployment.

```bash
# Navigate to the newly generated survey directory
cd surveys/survey-<survey_name>

# Run the Dash application
python app.py
```

**Example:**
```bash
cd surveys/survey-stated_preference_example
python app.py
```

Then, open your web browser and navigate to `http://127.0.0.1:8050/` (or the port specified in the terminal) to preview your survey!


## 🚀 Production Deployment (Docker + HTTPS)

Once your survey is generated and tested locally, you can prepare it for deployment on a Linux server using Docker and Gunicorn with SSL support.

### 1. Generate Container Files
Run the container generator by providing the `<survey_name>` and the domain name where it will be hosted:

```bash
python -m pixelsurvey-core.container_gen <survey_name> survey.example.com
```
This will inject a `Dockerfile` and a `docker-compose.yaml` (v3.8) directly into your survey folder.

### 2. Configure HTTPS (Certbot)
Before starting the container, ensure you have the Let's Encrypt certificates on your host machine. You can use Certbot on your Linux server:

```bash
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --standalone -d survey.example.com
```
Certbot will save the certificates in `/etc/letsencrypt/live/survey.example.com/`, which is the path automatically mapped by the generated `docker-compose.yaml`.

### 3. Launch the Application
Upload the survey folder to your server and run:

```bash
# Build the Docker image
docker compose build

# Start the service in the background
docker compose up -d
```

### 🛠️ Deployment Notes
- **Static Assets:** The `docker-compose.yaml` includes a commented-out volume for `/wd/assets/images`. If your survey relies on a large local image library, you can uncomment this line to mount a host directory instead of including the images in the Docker build.
- **Security:** The container uses the `python:3.11-slim-bullseye` base image to keep the environment lightweight and secure.
- **Port Mapping:** By default, the application maps port 443 (HTTPS) from the host to the container. Ensure your server's firewall allows traffic on this port.


---
*Built for research with [PixelSurvey](https://github.com/PixelSurvey/pixelsurvey-core).*

