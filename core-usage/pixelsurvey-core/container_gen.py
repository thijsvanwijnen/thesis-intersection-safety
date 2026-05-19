import sys
import os

# Add the directory containing this script to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.general.container_gen import ContainerGenerator

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m pixelsurvey-core.container_gen <survey_id> [domain_name]")
        print("Example: python -m pixelsurvey-core.container_gen my-survey survey.example.com")
        sys.exit(1)

    survey_id = sys.argv[1]
    domain_name = sys.argv[2] if len(sys.argv) > 2 else "example.com"

    try:
        cg = ContainerGenerator(survey_id)
        cg.generate_docker_files(domain_name=domain_name)
        print("\nSuccess! Your survey is ready for Docker deployment.")
        print(f"Check the files in surveys/survey-{survey_id}/")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
