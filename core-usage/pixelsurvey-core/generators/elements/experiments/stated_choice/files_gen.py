import random as rnd
import pandas as pd


class FilesGen:
    """Generates files for the stated choice experiment."""

    def __init__(self, experiment_data):# SCExperimentParser):
        self.experiment_data = experiment_data

    
    def generate_example_attributes_values_csv(self, output_dir="."):
        """Generate an example CSV for the attribute values."""
        attribs = self.experiment_data.get_attributes_variable_names_types()
        data = []
        for name, atype in attribs:
            for i in range(3):
                if atype == 'standard':
                    data.append({'attribute_name': name, 'attribute_value': 20*(i+1)})
                elif atype == 'image':
                    data.append({'attribute_name': name, 'attribute_value': f"https://example.com/image_{i+1}.png"})
        df = pd.DataFrame(data)
        df.to_csv(f"{output_dir}/example_sc_attributes_values.csv", index=False)

    
    def generate_example_experimental_design_csv(self, output_dir="."):
        """Generate example CSV for the experimental design."""
        exp_cols = self.experiment_data.get_experimental_design_columns()
        data = []
        index = 1
        for i in range(3):
            row = {'task_id': i+1, 'set_id': 1}
            for col in exp_cols:
                if 'url' in col:
                    row.update({col: f"https://example.com/img{index}.png"})
                    index += 1
                else:
                    row.update({col: 10})
            data.append(row)
        df = pd.DataFrame(data)
        df.to_csv(f"{output_dir}/example_sc_experimental_design.csv", index=False)


    def generate_random_experimental_design_csv(self, export = False, output_dir="."):
        """Generate a random experiment CSV based on attribute_values.csv"""
        values_path = self.experiment_data.settings_attributes_values_path
        df = pd.read_csv(values_path)

        attrib_names = self.experiment_data.get_attributes_variable_names_types()
        value_set = {}
        for an, _ in attrib_names:
            vset = df.loc[df['attribute_name'] == an, 'attribute_value'].to_list()
            value_set[an] = vset

        exp_cols = self.experiment_data.get_experimental_design_columns()
        data = []
        task_nr = 1
        for set_nr in range(self.experiment_data.settings_number_of_sets):
            for _ in range(self.experiment_data.settings_tasks_per_respondent):
                row = {'task_id': task_nr, 'set_id': set_nr + 1}
                task_nr += 1
                for col in exp_cols:
                    col_key = col.split('_', 2)[2]
                    row.update({col: rnd.choice(value_set[col_key])})
                data.append(row)
        df = pd.DataFrame(data)

        if export:
            df.to_csv(f"{output_dir}/random_sc_experimental_design.csv", index=False)
        return df
