import pandas as pd


class FilesGen:
    """Generates files for the Likert scale experiment."""

    def __init__(self, experiment_data): #LSExperimentParser):
        self.experiment_data = experiment_data

    
    def generate_example_instances_csv(self, output_dir="."):
        """Generate an example CSV for the instances."""
        data = []
        for i in range(3):
            row = {'instance': i+1}
            row.update({'img': f"https://example.com/im{i+1}.png"})
            data.append(row)

        df = pd.DataFrame(data)
        df.to_csv(f"{output_dir}/example_ls_instances.csv", index=False)

    
    def generate_example_experimental_design_csv(self, output_dir="."):
        """Generate example CSV for the experimental design."""
        exp_cols = self.experiment_data.get_experimental_design_columns()
        data = []
        index = 1
        for i in range(3):
            row = {'task_id': i+1, 'set_id': 1}
            for col in exp_cols:
                row.update({col: f"https://example.com/img{index}.png"})
                index += 1
            data.append(row)
        df = pd.DataFrame(data)
        df.to_csv(f"{output_dir}/example_ls_experimental_design.csv", index=False)


    def generate_random_experimental_design_csv(self, export = False, output_dir="."):
        """Generate a random experiment CSV based on instances.csv"""
        instances_path = self.experiment_data.settings_instances_path
        df = pd.read_csv(instances_path)

        exp_cols = self.experiment_data.get_experimental_design_columns()
        data = []
        task_nr = 1
        for set_nr in range(self.experiment_data.settings_number_of_sets):
            for _ in range(self.experiment_data.settings_tasks_per_respondent):
                row = {'task_id': task_nr, 'set_id': set_nr + 1}
                task_nr += 1
                for col in exp_cols:
                    row.update({col: df.sample(1)[col].iloc[0]})
                data.append(row)
        df = pd.DataFrame(data)

        if export:
            df.to_csv(f"{output_dir}/random_ls_experimental_design.csv", index=False)
        return df