from ..experiment_parser import ExperimentParser


class SCExperimentParser(ExperimentParser):
    """Parser for Stated Choice experiments"""
    def __init__(self, recipe_folder, experiment_data):
        super().__init__(recipe_folder, experiment_data)

    
    @property
    def experiment_type(self):
        """Experiment type (should be 'stated_choice')"""
        return self.experiment_data.get('experiment_type')
    

    @property
    def task_query(self):
        """Task configuration for stated choice"""
        return self.experiment_data['task']['query']
    

    @property
    def task_instance(self):
        """Task instance for the likert scale"""
        return self.experiment_data['task']['instance']


    @property
    def task_n_alternatives(self):
        """Number of alternatives for the stated choice task"""
        return self.experiment_data['task']['n_alternatives']


    @property
    def task_attributes(self):
        """Attributes for the stated choice task"""
        return self.experiment_data['task']['attributes']


    @property
    def settings_attributes_values_path(self):
        """Path to the attribute values for the stated choice experiment"""
        if self.settings_experimental_design_mode == 'random':
            path = self.recipe_folder / self.experiment_data['settings']['attributes_values']
            return path
        else:
            return None
    

    def get_settings_builder_path(self):
        """Get the settings builder file path for the experiment"""
        if self.settings_experimental_design_mode == 'custom':
            return self.settings_custom_design_path
        elif self.settings_experimental_design_mode == 'random':
            return self.settings_attributes_values_path


    def number_of_responses(self):
        """Number of responses for the stated choice task"""
        return self.settings_task_per_respondents
    

    @staticmethod
    def _var_name(label, atype):
        name = f"{label.lower().replace(' ', '_')}"
        if atype == 'image':
            name += "_url"
        return (name, atype)
    
    
    def get_experimental_design_columns(self):
        number_of_alternatives = self.task_n_alternatives
        c_name = lambda alt_n, att_n, label, atype: f"alt{alt_n}_att{att_n}_{SCExperimentParser._var_name(label, atype)[0]}"
        cols = [c_name(alt_n+1, att_n+1, att['label'], att['type']) for alt_n in range(number_of_alternatives) for att_n, att in enumerate(self.task_attributes)]
        return cols
    
    
    def get_attributes_variable_names_types(self):
        """Get variable names for the attributes in the stated choice task"""
        return [SCExperimentParser._var_name(att['label'], att['type']) for att in self.task_attributes]
    

    def has_image_attributes(self):
        """Check if the task has image attributes"""
        return any(attr['type'] == 'image' for attr in self.task_attributes)
    

    def has_standard_attributes(self):
        """Check if the task has standard attributes"""
        return any(attr['type'] == 'standard' for attr in self.task_attributes)