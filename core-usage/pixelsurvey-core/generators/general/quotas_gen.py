import pandas as pd


class QuotasGen:
    """Generates Quotas files."""

    def __init__(self, survey_data):
        self.survey_data = survey_data


    def generate_example_quotas_csv(self):
        """Generate an example CSV for the quotas."""
        cols, combs = self.survey_data.get_screening_questions_table()

        df = pd.DataFrame(combs, columns=cols)
        df['quota'] = 100
        df['actual'] = 0
        df.to_csv("example_quotas.csv", index=False)
    

    def generate_no_limit_quotas_csv(self, export=False):
        """Generate an example CSV for the quotas."""
        cols, combs = self.survey_data.get_screening_questions_table()

        df = pd.DataFrame(combs, columns=cols)
        df['quota'] = 9999 # Needs to be improved
        df['actual'] = 0

        if export:
            df.to_csv("quotas.csv", index=False)
        return df


    def generate_uniform_quotas_csv(self, export=False):
        """Generate an example CSV for the quotas."""
        cols, combs = self.survey_data.get_screening_questions_table()
        limit = self.survey_data.screening_quotas_limit

        df = pd.DataFrame(combs, columns=cols)
        df['quota'] = limit
        df['actual'] = 0

        if export:
            df.to_csv("quotas.csv", index=False)
        return df
    

    def generate_custom_quotas_csv(self, export=False):
        """Generate an example CSV for the quotas."""
        quotas_limits_path = self.survey_data.screening_quotas_limits_path
        df = pd.read_csv(quotas_limits_path)

        if export:
            df.to_csv("quotas.csv", index=False)
        return df
    
if __name__ == "__main__":
    
    from parsers.recipe_parser import RecipeParser as rp
    survey_data = rp("243bb3a3-bff2-4113-ae5a-1f3b92fdefda")
    qg = QuotasGen(survey_data)
    qg.generate_example_quotas_csv()