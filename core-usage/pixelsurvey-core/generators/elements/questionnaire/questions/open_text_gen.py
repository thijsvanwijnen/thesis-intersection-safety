import os
from jinja2 import Environment, FileSystemLoader

class OpenTextCard:
    """Open Text Question Generator"""
    
    def __init__(self, question_data):
        """
        Initialize with a single question data dictionary

        Args:
            question_data (dict): Single question with structure:
                {
                    'id': int,
                    'type': 'open_text',
                    'order': int,
                    'question': str,
                    'required': bool,
                    'variable_name': str
                }
        """
        self.question_data = question_data


    def generate(self):
        """Generate the open text question card element"""
        question_id = self.question_data['id']
        question_text = self.question_data['question']
        required = self.question_data['required']
        
        # Add required indicator to question text
        question_display = question_text
        if required:
            question_display += " *"
            
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        template = env.get_template('open_text.py.jinja')
        
        card_code = template.render(
            question_id=question_id,
            question_display=question_display,
            required="True" if required else "False"
        )
        
        return card_code
