import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import vars as v

class ContainerGenerator:
    def __init__(self, survey_id):
        self.survey_id = survey_id
        self.survey_folder = Path(f"{v.SURVEYS_DIR}/survey-{survey_id}")
        
        # Template setup
        template_dir = os.path.join(os.path.dirname(__file__), "container_templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_docker_files(self, domain_name="example.com"):
        """Generates Dockerfile and docker-compose.yaml in the survey folder."""
        if not self.survey_folder.exists():
            raise FileNotFoundError(f"Survey folder not found: {self.survey_folder}")

        # Render Dockerfile
        dockerfile_template = self.env.get_template("Dockerfile.jinja")
        dockerfile_content = dockerfile_template.render(domain_name=domain_name)
        
        # Render docker-compose
        compose_template = self.env.get_template("docker-compose.yaml.jinja")
        compose_content = compose_template.render(survey_id=self.survey_id)

        # Write files
        with open(self.survey_folder / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        with open(self.survey_folder / "docker-compose.yaml", "w") as f:
            f.write(compose_content)

        print(f"Docker files generated in: {self.survey_folder}")
