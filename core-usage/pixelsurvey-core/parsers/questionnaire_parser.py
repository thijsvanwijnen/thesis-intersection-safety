class QuestionnaireParser:
    """Parser for questionnaire activities"""

    def __init__(self, recipe_folder, questionnaire_data):
        self.recipe_folder = recipe_folder
        self.questionnaire_data = questionnaire_data


    @property
    def type(self):
        """Type of the activity"""
        return 'questionnaire'


    @property
    def order(self):
        """Order of the activity in the sequence"""
        return self.questionnaire_data['order']
    

    @property 
    def persistent_instructions(self):
        """Persistent instructions shown throughout the activity"""
        return self.questionnaire_data['persistent_instructions']


    @property
    def questions(self):
        """List of questionnaire questions"""
        return self.questionnaire_data['questions']


    def get_response_db_columns(self):
        """Get database columns for questionnaire questions"""
        column_name = lambda order: f'act{self.order}_q{order}'
        questions = self.questions
        return [column_name(q['order']) for q in questions]
    

    def get_activity_key(self):
        """Get the activity key for the questionnaire"""
        return f'act{self.order}'
