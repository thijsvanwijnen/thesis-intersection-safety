import os
from jinja2 import Environment, FileSystemLoader

class StatedChoiceCard:
    """Stated Choice Experiment Card Generator"""
    
    def __init__(self, experiment_data):
        """Initialize with experiment data"""
        self.experiment_data = experiment_data
        self.image_attributes = experiment_data.has_image_attributes()
        self.standard_attributes = experiment_data.has_standard_attributes()

    def generate_page(self, activity_key, experiment_name, n_act_tasks, n_prev_tasks, n_total_tasks, activity_button_id):
        # Load Jinja2 template
        template_dir = os.path.dirname(__file__)
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(template_dir))), "pages")
        
        env = Environment(loader=FileSystemLoader([template_dir, pages_dir]))
        env.globals.update(enumerate=enumerate)
        template = env.get_template('template.py.jinja')
        
        variable_names = self.experiment_data.get_experimental_design_columns()
        task_attrs = self.experiment_data.task_attributes
        n_attrs = len(task_attrs)
        
        # Prepare attributes for each alternative
        alt_attributes = []
        for alt_n in range(self.experiment_data.task_n_alternatives):
            current_alt_attrs = []
            for i, attr in enumerate(task_attrs):
                a = attr.copy()
                # Get the variable name from the flattened list
                a['variable_name'] = variable_names[i + (alt_n * n_attrs)]
                current_alt_attrs.append(a)
            alt_attributes.append(current_alt_attrs)

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
            variable_names=variable_names,
            alt_attributes=alt_attributes,
            image_attributes=self.image_attributes,
            standard_attributes=self.standard_attributes
        )
        
        return page_code
