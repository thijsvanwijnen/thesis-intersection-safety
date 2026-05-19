import os
from jinja2 import Environment, FileSystemLoader

class LikertScaleCard:
    def __init__(self, question_data):
        self.question_data = question_data

    def generate(self):
        """Renders the HTML/Dash card"""
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        template = env.get_template('likert_scale.py.jinja')
        return template.render(
            question_id=self.question_data['id'],
            question=self.question_data['question'],
            likert_scale=self.question_data['likert_scale'],
            evaluations=self.question_data['evaluations']
        )

    def generate_callbacks(self):
        """Logic to join multiple inputs into one string (separated by /)"""
        qid = self.question_data['id']
        n_items = len(self.question_data['evaluations'])
        
        # Pre-build the list of Inputs for Dash
        inputs = ", ".join([f"Input('question-{qid}-{i}', 'value')" for i in range(n_items)])
        
        return f"""
@callback(
    Output('question-{qid}', 'value'),
    [{inputs}],
    prevent_initial_call=True
)
def aggregate_likert_{qid}(*values):
    if all(v is not None for v in values):
        return '/'.join([str(v) for v in values])
    return None
"""
