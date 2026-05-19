from ..experiment_parser import ExperimentParser


class SJExperimentParser(ExperimentParser):
    """Parser for Similarity Judgment experiments"""
    
    def __init__(self, recipe_folder, experiment_data):
        super().__init__(recipe_folder, experiment_data)


    @property
    def experiment_type(self):
        """Experiment type (should be 'similarity_judgment')"""
        return self.experiment_data.get('experiment_type')
    

    @property
    def task_query(self):
        """Task configuration for similarity judgment"""
        return self.experiment_data['task']['query']
    
    
    @property
    def task_instance(self):
        """Task instance for the likert scale"""
        return self.experiment_data['task']['instance']
    

    @property
    def task_images_per_instance(self):
        """Number of images per similarity judgment instance"""
        return self.experiment_data['task']['images_per_instance']
    
    
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
    

    def number_of_responses(self):
        """Number of responses for the similarity judgment task"""
        return self.settings_task_per_respondents
    

    def get_experimental_design_columns(self):
        images_per_instance = self.task_images_per_instance
        c_name = lambda opt_n, img_n: f"alt{opt_n}_img{img_n}"
        cols = [c_name(alt_n+1, img_n+1) for alt_n in range(3) for img_n in range(images_per_instance)]
        return cols