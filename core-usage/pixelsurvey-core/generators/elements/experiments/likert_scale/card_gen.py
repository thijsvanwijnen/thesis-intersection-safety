import os
from jinja2 import Environment, FileSystemLoader

class LikertScaleCard:
    """Likert Scale Experiment Card Generator"""
    
    def __init__(self, experiment_data):
        """Initialize with experiment data"""
        self.experiment_data = experiment_data

    def generate_page(self, activity_key, experiment_name, n_act_tasks, n_prev_tasks, n_total_tasks, activity_button_id):
        # Load Jinja2 template
        template_dir = os.path.dirname(__file__)
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(template_dir))), "pages")
        
        env = Environment(loader=FileSystemLoader([template_dir, pages_dir]))
        env.globals.update(enumerate=enumerate)
        template = env.get_template('template.py.jinja')
        
        page_code = template.render(
            activity_key=activity_key,
            experiment_name=experiment_name,
            n_act_tasks=n_act_tasks,
            n_prev_tasks=n_prev_tasks,
            n_total_tasks=n_total_tasks,
            experiment_instructions=self.experiment_data.persistent_instructions,
            experiment_button_id=activity_button_id,
            act_order=self.experiment_data.order,
            task_query=self.experiment_data.task_query,
            instance=self.experiment_data.task_instance,
            likert_scale=self.experiment_data.task_likert_scale,
            evaluations=self.experiment_data.task_evaluations,
            variable_names=self.experiment_data.get_experimental_design_columns()
        )
        
        return page_code
