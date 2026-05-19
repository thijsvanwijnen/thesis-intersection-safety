class ExperimentParser:
    """Parser for experiment activities"""

    def __new__(cls, recipe_folder, experiment_data):
        """Factory constructor that returns the appropriate subclass"""
        if cls is not ExperimentParser:
            # If called from a subclass, use normal constructor
            return super().__new__(cls)
        
        # If called from ExperimentParser, detect type and return appropriate subclass
        from .experiment_parsers.sc_experiment_parser import SCExperimentParser
        from .experiment_parsers.sj_experiment_parser import SJExperimentParser
        from .experiment_parsers.ls_experiment_parser import LSExperimentParser
        
        experiment_type = experiment_data['experiment_type']
        
        if experiment_type == 'stated_choice':
            return SCExperimentParser(recipe_folder, experiment_data)
        elif experiment_type == 'similarity_judgment':
            return SJExperimentParser(recipe_folder, experiment_data)
        elif experiment_type == 'likert_scale':
            return LSExperimentParser(recipe_folder, experiment_data)
        else:
            raise ValueError(f"Unknown experiment type: {experiment_type}")
    
    
    def __init__(self, recipe_folder, experiment_data):
        """Initialize with experiment data"""
        self.recipe_folder = recipe_folder
        self.experiment_data = experiment_data

    
    @property
    def type(self):
        """Type of the activity"""
        return 'experiment'


    @property
    def order(self):
        """Order of the activity in the sequence"""
        return self.experiment_data['order']


    @property
    def experiment_type(self):
        """Activity type (experiment or questionnaire)"""
        return self.experiment_data['experiment_type']


    @property 
    def persistent_instructions(self):
        """Persistent instructions shown throughout the activity"""
        return self.experiment_data['persistent_instructions']
    

    @property
    def settings_tasks_per_respondent(self):
        """Number of tasks per respondent for the activity"""
        return self.experiment_data['settings']['tasks_per_respondent']
    

    @property
    def settings_experimental_design_mode(self):
        """Experimental design mode for the activity"""
        return self.experiment_data['settings']['experimental_design_mode']
    

    @property
    def settings_number_of_sets(self):
        """Number of sets for the activity"""
        return self.experiment_data['settings']['number_of_sets']


    @property
    def settings_custom_design_path(self):
        """Path to the custom experimental design"""
        if self.settings_experimental_design_mode == 'custom':
            return self.recipe_folder / self.experiment_data['settings']['custom_design']
        elif self.settings_experimental_design_mode == 'random':
            return None
        else:
            return None
    

    def get_response_db_columns(self):
        """Get database columns for experiment questions"""
        column_name = lambda order: f'act{self.order}_t{order}'
        n_tasks = self.settings_tasks_per_respondent
        return [column_name(i) for i in range(1, n_tasks + 1)]
    
    
    def get_task_ids(self):
        """Get task columns for the likert scale task"""
        return [f'act{self.order}_task_{i}' for i in range(1, self.settings_tasks_per_respondent + 1)]


    def get_activity_key(self):
        """Get the activity key for the experiment"""
        return f'act{self.order}'