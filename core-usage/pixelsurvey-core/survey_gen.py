import os
import sys
import shutil
import os
from pathlib import Path

# Add the directory containing this script to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vars as v
from generators.database.queries_gen import QueriesGenerator as QGEN
from generators.elements.experiments.stated_choice.card_gen import StatedChoiceCard as SCCard
from generators.elements.experiments.similarity_judgment.card_gen import SimilarityJudgmentCard as SJCard
from generators.elements.experiments.likert_scale.card_gen import LikertScaleCard as LSCard

EXPERIMENT_REGISTRY = {
    "stated_choice": SCCard,
    "similarity_judgment": SJCard,
    "likert_scale": LSCard
}

class SurveyGenerator:
    def __init__(self, survey_id):
        """Initialize with survey ID"""
        self.survey_id = survey_id
        self.survey_path = Path(f"{v.SURVEYS_DIR}/survey-{self.survey_id}")


    def create_folders(self):
        """Create survey folder structure: survey_id/assets/logos/ and survey_id/pages/"""

        # Create main survey folder if doesn't exist
        os.makedirs(v.SURVEYS_DIR, exist_ok=True)

        folders = [
            self.survey_path,
            self.survey_path / "assets",
            self.survey_path / "assets" / "logos",
            self.survey_path / "pages"
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"Created: {folder}")
        
        print(f"Survey '{self.survey_id}' folder structure complete!")


    def allocate_pixelsurvey_logo(self, source_filepath = v.PIXELSURVEY_LOGO):
        """Allocate the PixelSurvey logo to the appropriate folder"""

        dest_path = self.survey_path / "assets" / "logos" / "pixelsurvey_logo.png"
        shutil.copy2(source_filepath, dest_path)
        print(f"Allocated PixelSurvey logo: {source_filepath} → {dest_path}")
        return dest_path.relative_to(self.survey_path)


    def allocate_user_logo(self, source_filepath):
        """Allocate the user logo to the appropriate folder"""

        dest_path = self.survey_path / "assets" / "logos" / "user_logo.png"
        shutil.copy2(source_filepath, dest_path)
        print(f"Allocated user logo: {source_filepath} → {dest_path}")
        return dest_path.relative_to(self.survey_path)
    

    def generate_app_py(self, 
                        survey_title, 
                        survey_subtitle,
                        user_logo_path, 
                        pixelsurvey_logo_path, 
                        survey_color,
                        pixelsurvey_version,
                        pixelsurvey_version_name,
                        survey_data):
        """Generate app.py file from template with survey configuration"""
        
        # Read the template file
        with open(v.APP_TEMPLATE, "r", encoding='utf-8') as f:
            app_template = f.read()

        act_keys = survey_data.get_experimental_activity_tasks_count().keys()
        store = lambda act: f'dcc.Store(id = "last_task_resp_{act}", data = {{"task": None}}, storage_type = "session")'
        temp_act_stores = ",\n\t".join([store(act) for act in act_keys])

        # Replace placeholders using our custom $variable$ convention
        app_content = app_template.replace("$survey_id$", self.survey_id)
        app_content = app_content.replace("$survey_title$", survey_title)
        app_content = app_content.replace("$survey_subtitle$", survey_subtitle)
        app_content = app_content.replace("$user_logo_path$", str(user_logo_path).replace("\\", "/"))
        app_content = app_content.replace("$pixelsurvey_logo_path$", str(pixelsurvey_logo_path).replace("\\", "/"))
        app_content = app_content.replace("$survey_color$", survey_color)
        app_content = app_content.replace("$pixelsurvey_version$", str(pixelsurvey_version))
        app_content = app_content.replace("$pixelsurvey_version_name$", pixelsurvey_version_name)
        app_content = app_content.replace("$temp_act_stores$", temp_act_stores)

        # Write to app.py file
        app_file_path = self.survey_path / "app.py"
        with open(app_file_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        print(f"Generated app.py at: {app_file_path}")
        return app_file_path


    def generate_requirements_txt(self):
        """Generate requirements.txt file with app dependencies"""
        requirements_content = (
            "dash>=3.0.0\n"
            "dash-bootstrap-components>=1.0.0\n"
            "pandas>=2.0.0\n"
            "gunicorn>=21.0.0\n"
        )
        requirements_file_path = self.survey_path / "requirements.txt"
        with open(requirements_file_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"Generated requirements.txt at: {requirements_file_path}")
        return requirements_file_path


    def generate_database_db(self):
        """Generate database.db file from template with survey configuration"""
        pass


    def generate_database_py(self):
        """Generate database.py file from template with survey configuration"""
        
        # Read the template file
        with open(v.DATABASE_TEMPLATE, "r", encoding='utf-8') as f:
            database_template = f.read()
        
        qgen = QGEN(self.survey_id)
        screening_write_query = qgen.gen_screening_write_query()
        quotas_read_query = qgen.gen_quotas_read_query()
        quotas_write_query = qgen.gen_quotas_write_query()
        screening_read_query = qgen.gen_screening_read_query()

        database_content = database_template.replace("$screening_write_query$", screening_write_query)
        database_content = database_content.replace("$quotas_read_query$", quotas_read_query)
        database_content = database_content.replace("$quotas_write_query$", quotas_write_query)
        database_content = database_content.replace("$screening_read_query$", screening_read_query)

        # Write to database.py file
        database_file_path = self.survey_path / "database.py"
        with open(database_file_path, 'w', encoding='utf-8') as f:
            f.write(database_content)

        print(f"Generated database.py at: {database_file_path}")
        return database_file_path


    def generate_home_py(self, home_content, home_button_id):
        """Generate home.py page from template with content"""
        
        # Read the template file
        with open(v.HOME_TEMPLATE, "r", encoding='utf-8') as f:
            home_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        home_page_content = home_template.replace("$home_content$", home_content)
        home_page_content = home_page_content.replace("$home_button_id$", home_button_id)

        # Write to pages/home.py file
        home_file_path = self.survey_path / "pages" / "home.py"
        with open(home_file_path, 'w', encoding='utf-8') as f:
            f.write(home_page_content)
        
        print(f"Generated home.py at: {home_file_path}")
        return home_file_path
    

    def generate_consent_py(self, consent_content, consent_statement, task_counts, consent_button_id, survey_hrefs):
        """Generate consent.py page from template with content and statement"""

        # Read the template file
        with open(v.CONSENT_TEMPLATE, "r", encoding='utf-8') as f:
            consent_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        consent_page_content = consent_template.replace("$consent_content$", consent_content)
        consent_page_content = consent_page_content.replace("$consent_statement$", consent_statement)
        consent_page_content = consent_page_content.replace("$tasks_counts_dict$", str(task_counts))
        consent_page_content = consent_page_content.replace("$consent_button_id$", consent_button_id)
        consent_page_content = consent_page_content.replace("$survey_hrefs$", str(survey_hrefs))

        # Write to pages/consent.py file
        consent_file_path = self.survey_path / "pages" / "consent.py"
        with open(consent_file_path, 'w', encoding='utf-8') as f:
            f.write(consent_page_content)
        
        print(f"Generated consent.py at: {consent_file_path}")
        return consent_file_path


    def generate_screening_py(self, screening_content, num_screening_questions, screening_questions_code, screening_callbacks_code, screening_button_id):
        """Generate screening.py page from template with content and questions"""
        
        # Read the template file
        with open(v.SCREENING_TEMPLATE, "r", encoding='utf-8') as f:
            screening_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        screening_page_content = screening_template.replace("$screening_content$", screening_content)
        screening_page_content = screening_page_content.replace("$screening_questions$", screening_questions_code)
        screening_page_content = screening_page_content.replace("$screening_callbacks$", screening_callbacks_code)
        screening_page_content = screening_page_content.replace("$screening_button_id$", screening_button_id)
        screening_page_content = screening_page_content.replace("$num_screening_questions$", str(num_screening_questions))

        # Write to pages/screening.py file
        screening_file_path = self.survey_path / "pages" / "screening.py"
        with open(screening_file_path, 'w', encoding='utf-8') as f:
            f.write(screening_page_content)
        
        print(f"Generated screening.py at: {screening_file_path}")
        return screening_file_path
    

    def generate_fullquota_py(self, fullquota_content):
        """Generate fullquota.py page from template"""

        # Read the template file
        with open(v.FULLQUOTA_TEMPLATE, "r", encoding='utf-8') as f:
            fullquota_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        fullquota_page_content = fullquota_template.replace("$fullquota_content$", fullquota_content)

        # Write to pages/fullquota.py file
        fullquota_file_path = self.survey_path / "pages" / "fullquota.py"
        with open(fullquota_file_path, 'w', encoding='utf-8') as f:
            f.write(fullquota_page_content)

        print(f"Generated fullquota.py at: {fullquota_file_path}")
        return fullquota_file_path


    def generate_instructions_py(self, instructions_content, instructions_button_id, first_activity_href):
        """Generate instructions.py page from template with content and button ID"""

        # Read the template file
        with open(v.INSTRUCTIONS_TEMPLATE, "r", encoding='utf-8') as f:
            instructions_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        instructions_page_content = instructions_template.replace("$instructions_content$", instructions_content)
        instructions_page_content = instructions_page_content.replace("$instructions_button_id$", instructions_button_id)
        instructions_page_content = instructions_page_content.replace("$first_activity_href$", first_activity_href)

        # Write to pages/instructions.py file
        instructions_file_path = self.survey_path / "pages" / "instructions.py"
        with open(instructions_file_path, 'w', encoding='utf-8') as f:
            f.write(instructions_page_content)

        print(f"Generated instructions.py at: {instructions_file_path}")
        return instructions_file_path
    

    def generate_experiment_py(self, activity_key, experiment_data, survey_data, activity_button_id):
        """Generate activity_i.py page from template with content"""

        experiment_name = f"{experiment_data.order}_{experiment_data.experiment_type}"
        n_act_tasks = experiment_data.settings_tasks_per_respondent
        n_prev_tasks = survey_data.get_previous_activity_tasks_count(experiment_data.order)
        n_total_tasks = survey_data.get_total_tasks_count()

        if experiment_data.experiment_type in EXPERIMENT_REGISTRY:
            CardClass = EXPERIMENT_REGISTRY[experiment_data.experiment_type]
            card = CardClass(experiment_data)
            
            experiment_page_content = card.generate_page(
                activity_key=activity_key,
                experiment_name=experiment_name,
                n_act_tasks=n_act_tasks,
                n_prev_tasks=n_prev_tasks,
                n_total_tasks=n_total_tasks,
                activity_button_id=activity_button_id
            )
        else:
            print(f"Warning: Experiment type '{experiment_data.experiment_type}' not found in registry.")
            return None

        # Write to pages/activity_key.py file
        experiment_file_path = self.survey_path / "pages" / f"{activity_key}.py"
        with open(experiment_file_path, 'w', encoding='utf-8') as f:
            f.write(experiment_page_content)

        print(f"Generated {activity_key}.py at: {experiment_file_path}")
        return experiment_file_path
    

    def generate_questionnaire_py(self, activity_key, questionnaire_instructions, activity_order, survey_data, num_questionnaire_questions, questionnaire_questions_code, questionnaire_callbacks_code, questionnaire_button_id):
        """Generate questionnaire.py page from template with content and questions"""

        # Read the template file
        with open(v.QUESTIONNAIRE_TEMPLATE, "r", encoding='utf-8') as f:
            questionnaire_template = f.read()

        n_prev_tasks = survey_data.get_previous_activity_tasks_count(activity_order)
        n_total_tasks = survey_data.get_total_tasks_count()
        questionnaire_progress = int(round(( (n_prev_tasks+1) / n_total_tasks) * 100, 0)) 
        if questionnaire_progress == 100:
            questionnaire_progress = 99

        # Replace placeholders using our custom $variable$ convention
        questionnaire_page_content = questionnaire_template.replace('$activity_key$', activity_key)
        questionnaire_page_content = questionnaire_page_content.replace("$questionnaire_content$", questionnaire_instructions)
        questionnaire_page_content = questionnaire_page_content.replace("$questionnaire_questions$", questionnaire_questions_code)
        questionnaire_page_content = questionnaire_page_content.replace("$questionnaire_button_id$", questionnaire_button_id)
        questionnaire_page_content = questionnaire_page_content.replace("$questionnaire_callbacks$", questionnaire_callbacks_code)
        questionnaire_page_content = questionnaire_page_content.replace("$num_questionnaire_questions$", str(num_questionnaire_questions))
        questionnaire_page_content = questionnaire_page_content.replace("$questionnaire_prev_progress$", str(questionnaire_progress))

        # Write to pages/activity_key.py file
        questionnaire_file_path = self.survey_path / "pages" / f"{activity_key}.py"
        with open(questionnaire_file_path, 'w', encoding='utf-8') as f:
            f.write(questionnaire_page_content)

        print(f"Generated {activity_key}.py at: {questionnaire_file_path}")
        return questionnaire_file_path


    def generate_end_py(self, end_content):
        """Generate end.py page from template"""

        # Read the template file
        with open(v.END_TEMPLATE, "r", encoding='utf-8') as f:
            end_template = f.read()

        # Replace placeholders using our custom $variable$ convention
        end_page_content = end_template.replace("$end_content$", end_content)

        # Write to pages/end.py file
        end_file_path = self.survey_path / "pages" / "end.py"
        with open(end_file_path, 'w', encoding='utf-8') as f:
            f.write(end_page_content)

        print(f"Generated end.py at: {end_file_path}")
        return end_file_path


# Example usage with SurveyRecipe
if __name__ == "__main__":
    from parsers.recipe_parser import RecipeParser
    from generators.database.database_gen import DatabaseGenerator
    from generators.elements.questionnaire.questionnaire_gen import QuestionnaireCards

    # Get survey_id from command line arguments or use default
    if len(sys.argv) < 2:
        print("Usage: python pixelsurvey-core/survey_gen.py <survey_id>")
        print("Example: python pixelsurvey-core/survey_gen.py safe-seoul-pilot-en-v1_3")
        sys.exit(1)
    
    survey_id = sys.argv[1]
    rp = RecipeParser(survey_id)
    sg = SurveyGenerator(survey_id)
    dg = DatabaseGenerator(survey_id)

    # Folder creations
    sg.create_folders()

    # Allocate PixelSurvey logo
    ps_logo_path = sg.allocate_pixelsurvey_logo()

    # Allocate User logo
    user_logo_origin_path = rp.logo_path
    user_logo_path = sg.allocate_user_logo(user_logo_origin_path)

    # Generate database.db file
    dg.create_database_tables(
        screening_questions_db_columns=rp.get_screening_questions_db_columns(),
        activities_db_columns=rp.get_activities_db_columns(),
        activity_pages=rp.activity_pages
    )

    # Populate the database tables and generate db manager
    dg.populate_database_tables(rp)
    sg.generate_database_py()

    # Generate app.py using recipe metadata
    sg.generate_requirements_txt()
    sg.generate_app_py(
        user_logo_path=user_logo_path,
        pixelsurvey_logo_path=ps_logo_path,
        survey_title=rp.title,
        survey_subtitle=rp.subtitle,
        survey_color=rp.color,
        pixelsurvey_version=rp.version,
        pixelsurvey_version_name=rp.version_name,
        survey_data=rp
    )

    page_buttons = rp.get_button_sequence()

    # PAGES
    
    # Generate home.py based on the home template
    sg.generate_home_py(rp.home_content, page_buttons['home'])

    # Generate consent.py based on the consent template
    task_counts_dict = rp.get_experimental_activity_tasks_count()
    survey_hrefs = rp.get_href_sequence()
    sg.generate_consent_py(rp.consent_content, 
                           rp.consent_statement, 
                           task_counts_dict,
                           page_buttons['consent'],
                           survey_hrefs)

    # Generate screening.py based on the screening template
    questions_list = rp.screening_questions.questions
    questions_cards, questions_callbacks = QuestionnaireCards.generate_questionnaire_content(questions_list)
    sg.generate_screening_py(rp.screening_content, len(questions_list), questions_cards, questions_callbacks, page_buttons['screening'])

    # Generate fullquota.py based on the fullquota template
    sg.generate_fullquota_py(rp.screening_fullquota_content)

    # Generate instructions.py based on the instructions template
    first_activity_href = survey_hrefs['/instructions']
    sg.generate_instructions_py(rp.instructions_content, page_buttons['instructions'], first_activity_href)

    # Generate activity pages
    for activity in rp.activity_pages:
        activity_key = activity.get_activity_key()
        if activity.type == 'experiment':
            sg.generate_experiment_py(activity_key, activity, rp, page_buttons[activity_key])
        else:
            questionnaire_list = activity.questions
            questionnaire_cards, questionnaire_callbacks = QuestionnaireCards.generate_questionnaire_content(questionnaire_list)
            sg.generate_questionnaire_py(activity_key, activity.persistent_instructions, activity.order, rp, len(questionnaire_list), questionnaire_cards, questionnaire_callbacks, page_buttons[activity_key])

    sg.generate_end_py(rp.end_content)