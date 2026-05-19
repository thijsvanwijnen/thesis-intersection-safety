import os
import sys
from pathlib import Path

# Add the directory containing this script to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.recipe_parser import RecipeParser
from generators.elements.experiments.stated_choice.files_gen import FilesGen as SCFilesGen
from generators.elements.experiments.similarity_judgment.files_gen import FilesGen as SJFilesGen
from generators.elements.experiments.likert_scale.files_gen import FilesGen as LSFilesGen

FILES_GEN_REGISTRY = {
    "stated_choice": SCFilesGen,
    "similarity_judgment": SJFilesGen,
    "likert_scale": LSFilesGen,
    "standard_stated_choice": SCFilesGen  # Reuses SC logic
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m pixelsurvey-core.experiment_templates_gen <survey_id> [--random]")
        sys.exit(1)

    survey_id = sys.argv[1]
    gen_random = "--random" in sys.argv
    
    try:
        rp = RecipeParser(survey_id)
        recipe_templates_dir = rp.recipe_folder / "templates"
        recipe_templates_dir.mkdir(exist_ok=True)
        
        print(f"Generating templates for recipe: {survey_id}")
        print(f"Output directory: {recipe_templates_dir}")

        for activity in rp.activity_pages:
            if activity.type == 'experiment':
                exp_type = activity.experiment_type
                mode = activity.settings_experimental_design_mode
                
                if exp_type in FILES_GEN_REGISTRY:
                    print(f"  - Processing activity {activity.order} ({exp_type}) in {mode} mode...")
                    fgen_class = FILES_GEN_REGISTRY[exp_type]
                    fgen = fgen_class(activity)
                    
                    if exp_type in ["stated_choice", "standard_stated_choice"]:
                        if mode == "custom":
                            print(f"    * Generating experimental design template...")
                            fgen.generate_example_experimental_design_csv(output_dir=recipe_templates_dir)
                        elif mode == "random":
                            print(f"    * Generating attributes values template...")
                            fgen.generate_example_attributes_values_csv(output_dir=recipe_templates_dir)
                    
                    elif exp_type in ["likert_scale", "similarity_judgment"]:
                        if mode == "custom":
                            print(f"    * Generating experimental design template...")
                            fgen.generate_example_experimental_design_csv(output_dir=recipe_templates_dir)
                        elif mode == "random":
                            print(f"    * Generating instances template...")
                            fgen.generate_example_instances_csv(output_dir=recipe_templates_dir)
                    
                    # Generate Random Design if requested
                    if gen_random and mode == "random":
                        print(f"    * Generating random experimental design from your values...")
                        try:
                            fgen.generate_random_experimental_design_csv(export=True, output_dir=recipe_templates_dir)
                        except Exception as re:
                            print(f"      [!] Skip random design generation: {re} (Check if your values CSV exists)")
                else:
                    print(f"  [!] Warning: No FilesGen registered for experiment type '{exp_type}'")

        print("\nSuccess! Templates generated in the 'templates/' folder of your recipe.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
