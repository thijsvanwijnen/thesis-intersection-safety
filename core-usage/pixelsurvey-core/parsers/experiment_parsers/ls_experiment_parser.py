from ..experiment_parser import ExperimentParser


class LSExperimentParser(ExperimentParser):
    """Parser for Likert Scale experiments"""
    
    def __init__(self, recipe_folder, experiment_data):
        super().__init__(recipe_folder, experiment_data)


    @property
    def experiment_type(self):
        """Experiment type (should be 'likert_scale')"""
        return self.experiment_data['experiment_type']
    

    @property
    def task_query(self):
        """Task configuration for likert scale"""
        return self.experiment_data['task']['query']


    @property
    def task_instance(self):
        """Task instance for the likert scale"""
        return self.experiment_data['task']['instance']


    @property
    def task_likert_scale(self):
        """Likert scale configuration for the task"""
        return self.experiment_data['task']['likert_scale']
    
    
    @property
    def task_evaluations(self):
        """Evaluations for the likert scale task"""
        return self.experiment_data['task']['evaluations']
    
    
    @property
    def settings_instances_path(self):
        """Path to the instances for the stated choice experiment"""
        if self.settings_experimental_design_mode == 'random':
            path = self.recipe_folder / self.experiment_data['settings']['instances']
            return path
        else:
            return None
    
    
    def get_settings_builder_path(self):
        """Get the settings builder file path for the experiment"""
        if self.settings_experimental_design_mode == 'custom':
            return self.settings_custom_design_path
        elif self.settings_experimental_design_mode == 'random':
            return self.settings_instances_path
    
    
    def get_number_of_responses(self):
        """Number of responses for the likert scale task"""
        return len(self.task_evaluations)*self.settings_task_per_respondents
    
    
    def get_experimental_design_columns(self):
        return ['img']

