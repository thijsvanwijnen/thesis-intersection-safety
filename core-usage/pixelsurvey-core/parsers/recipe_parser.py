import yaml
import itertools
from pathlib import Path

import vars as v
from .questionnaire_parser import QuestionnaireParser
from .experiment_parser import ExperimentParser


class RecipeParser:
    """Survey Recipe Reader - Parses YAML configuration files from recipes folder"""
    
    def __init__(self, survey_id):
        """Initialize with path to YAML file"""
        self.survey_id = survey_id
        self.recipe_folder = Path(f"{v.RECIPES_DIR}/recipe-{self.survey_id}")
        self.assets_folder = self.recipe_folder / "assets"
        self.experiment_folder = self.recipe_folder / "experiments"
        self.yaml_path = self.recipe_folder / "survey.yaml"

        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")

        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
            

    @property
    def version(self):
        """PixelSurvey version"""
        return self.data['version']


    @property
    def version_name(self):
        """PixelSurvey version name"""
        return self.data['version_name']


    @property
    def name(self):
        """Survey name/ID"""
        return self.data['survey']['name']
    

    @property
    def title(self):
        """Survey title"""
        return self.data['survey']['title']
    

    @property
    def subtitle(self):
        """Survey subtitle"""
        return self.data['survey']['subtitle']
    

    @property
    def logo_path(self):
        """Logo filename"""
        return self.recipe_folder / self.data['survey']['logo']
    

    @property
    def color(self):
        """Survey color theme in HEX format"""
        return self.data['survey']['color']
    

    #### HOME INPUTS ####
    @property
    def home_content(self):
        """Home page content (Markdown)"""
        home_data = self.data['survey']['sections']['onboarding']['home']
        return home_data['content']


    #### CONSENT INPUTS ####
    @property
    def consent_content(self):
        """Consent page content (Markdown)"""
        consent_data = self.data['survey']['sections']['onboarding']['consent']
        return consent_data['content']


    @property
    def consent_statement(self):
        """Consent checkbox statement"""
        consent_data = self.data['survey']['sections']['onboarding']['consent']
        return consent_data['consent_statement']


    #### SCREENING INPUTS ####
    @property
    def screening_content(self):
        """Screening page content (Markdown)"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        return screening_data['content']


    @property
    def screening_questions(self):
        """List of screening questions"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        screening_questionnaire = QuestionnaireParser(self.recipe_folder,screening_data)
        return screening_questionnaire
    

    @property
    def screening_quotas_method(self):
        """Screening quota method"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        return screening_data['quotas']['method']


    @property
    def screening_quotas_limit(self):
        """Screening quota limit for uniform quotas"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        return screening_data['quotas']['limit']


    @property
    def screening_quotas_limits_path(self):
        """Screening quotas filename"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        return self.recipe_folder / screening_data['quotas']['limits']
    
    @property
    def screening_fullquota_content(self):
        """Screening fullquota content (Markdown)"""
        screening_data = self.data['survey']['sections']['onboarding']['screening']
        return screening_data['quotas']['fullquota_content']


    #### INSTRUCTIONS INPUTS ####
    @property
    def instructions_content(self):
        """Instructions content (Markdown)"""
        instructions_data = self.data['survey']['sections']['body']['instructions']
        return instructions_data['content']
    

    #### ACTIVITIES INPUTS ####
    @property
    def activity_pages(self):
        """List of activities"""
        activities = [activity 
                      for key, activity 
                      in self.data['survey']['sections']['body'].items()
                      if key.startswith('activity_')
        ]

        sort_fn = lambda act: act['order'] if 'order' in act else float('inf')
        activities = sorted(activities, key=sort_fn)

        parser_fn = lambda act: ExperimentParser(self.recipe_folder, act) if act['type'] == 'experiment' else QuestionnaireParser(self.recipe_folder, act)
        activities = map(parser_fn, activities)

        return list(activities)


    #### END INPUTS ####
    @property
    def end_content(self):
        """End page content (Markdown)"""
        end_data = self.data['survey']['sections']['closure']['end']
        return end_data['content']


    # Utilitarian Methods
    def get_screening_questions_db_columns(self):
        """Get database columns for screening questions"""
        column_name = lambda order, name: f'sq{order}_{name}'
        screening_questions = self.screening_questions.questions
        return [column_name(q['order'], q['variable_name']) for q in screening_questions if 'variable_name' in q]


    def get_screening_questions_table(self):
        """Generate all possible combinations of screening question alternatives as DataFrame"""

        # Get column names and questions
        columns = self.get_screening_questions_db_columns()
        column_labels = [f"{c}_label" for c in columns]
        columns = column_labels + columns
        questions = self.screening_questions.questions
        
        # Extract alternatives for each question (only those with variable_name)
        alternatives_list = []
        for q in questions:
            if 'variable_name' in q and 'alternatives' in q:
                alternatives_id = [f"{alt}#id:{i+1}" for i, alt in enumerate(q['alternatives'])]
                alternatives_list.append(alternatives_id)

        combinations = list(itertools.product(*alternatives_list))
        rows = []
        for combo in combinations:
            labels = [c.split("#id:")[0] for c in combo]
            cols = [c.split("#id:")[1] for c in combo]
            rows.append((labels + cols))

        return columns, rows

    def get_activities_db_columns(self):
        """Get database columns for activities"""
        activity_columns = []
        for act in self.activity_pages:
            activity_columns.extend(act.get_response_db_columns())
        return activity_columns
    

    def get_experimental_activity_tasks_count(self):
        experiments = {}
        for act in self.activity_pages:
            if act.type == 'experiment':
                activity_key = f"act{act.order}"
                experiments[activity_key] = act.settings_tasks_per_respondent
        return experiments
    

    def get_total_activity_tasks_count(self):
        tasks = {}
        for act in self.activity_pages:
            if act.type == 'experiment':
                activity_key = f"act{act.order}"
                tasks[activity_key] = act.settings_tasks_per_respondent
            elif act.type == 'questionnaire':
                activity_key = f"act{act.order}"
                tasks[activity_key] = 1
        return tasks
    

    def get_total_tasks_count(self):
        return sum(self.get_total_activity_tasks_count().values())


    def get_previous_activity_tasks_count(self, activity_order):
        """Get previous activity tasks count"""
        return sum(self.get_total_activity_tasks_count()[f'act{n}'] for n in range(1, activity_order))


    def get_button_sequence(self):
        """Get button sequence for activities"""
        buttons = {'home': 'home-button',
                   'consent': 'consent-button',
                   'screening': 'screening-button',
                   'instructions': 'instructions-button'}

        for act in self.activity_pages:
            buttons.update({f'act{act.order}': f'act{act.order}-button'})

        buttons.update({'end': 'end-button'})

        return buttons
    

    def get_href_sequence(self):
        """Get href sequence for activities"""
        hrefs = {'/home': '/consent',
                  '/consent': '/screening',
                  '/screening': '/instructions'}

        root = '/instructions'
        for act in self.activity_pages:
            if act.type == 'experiment':
                for t in range(1, act.settings_tasks_per_respondent + 1):
                    hrefs.update({root: f'/act{act.order}/{t}'})
                    root = f'/act{act.order}/{t}'
            elif act.type == 'questionnaire':
                hrefs.update({root: f'/act{act.order}'})
                root = f'/act{act.order}'

        hrefs.update({root: '/end'})

        return hrefs