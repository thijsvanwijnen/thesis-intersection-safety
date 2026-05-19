import pandas as pd
import sqlite3 as sql
from pathlib import Path

import vars as v

# Quota
from ..general.quotas_gen import QuotasGen as qgen

# Experiments
from ..elements.experiments.stated_choice.files_gen import FilesGen as scgen
from ..elements.experiments.similarity_judgment.files_gen import FilesGen as sjgen
from ..elements.experiments.likert_scale.files_gen import FilesGen as lsgen

class DatabaseGenerator:
    def __init__(self, survey_id):
        self.database_path = Path(f"{v.SURVEYS_DIR}/survey-{survey_id}/database.db")
        self.screening_columns = None
        self.activities_columns = None
        self.experimental_activities = {}


    def _create_table(self, table_name: str, columns: dict):
        with sql.connect(self.database_path) as conn:
            c = conn.cursor()
            c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{k} {v}' for k, v in columns.items()])})")
            conn.commit()
    

    def _create_response_table(self):
        base_columns = {'respondent_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                        'set_id': 'INTEGER NOT NULL',
                        'external_id': 'TEXT'}

        screening_columns = {f'{sq_name}': 'TEXT' for sq_name in self.screening_columns}
        activities_columns = {f'{aq_name}': 'TEXT' for aq_name in self.activities_columns}
        response_columns = {**base_columns, **screening_columns, **activities_columns}

        self._create_table("Response", response_columns)


    def _create_quotas_table(self):
        counting_columns = {'quota': 'INTEGER',
                           'actual': 'INTEGER'}

        screening_label_columns = {f'{sq_name}_label': 'TEXT' for sq_name in self.screening_columns}
        screening_columns = {f'{sq_name}': 'TEXT' for sq_name in self.screening_columns}

        quota_columns = {**screening_label_columns, **screening_columns, **counting_columns}

        self._create_table("Quotas", quota_columns)

    
    def _create_experimental_tables(self, activities):
        for act in activities:
            if act.type == 'experiment':
                base_columns = {'task_id': 'INTEGER PRIMARY KEY AUTOINCREMENT'}
                exp_columns = act.get_experimental_design_columns()
                exp_columns = {f'{name}': 'TEXT' for name in exp_columns}
                columns = {**base_columns, **exp_columns}
                self._create_table(f"Act{act.order}_task", columns)
                self.experimental_activities[f"Act{act.order}_task"] = act
    

    def _create_task_set_table(self, activities):
        base_columns = {'set_id': 'INTEGER PRIMARY KEY AUTOINCREMENT'}
        task_columns = {}
        for act in activities:
            if act.type == 'experiment':
                columns_aux = act.get_task_ids()
                columns_aux = {f'{name}': 'INTEGER' for name in columns_aux}
                task_columns = {**task_columns, **columns_aux}
        columns = {**base_columns, **task_columns}
        self._create_table("Task_set", columns)


    def _create_timestamp_table(self, activities):
        base_columns = {'respondent_id': 'INTEGER NOT NULL',
                        'consent_button': 'DECIMAL',
                        'screening_button': 'DECIMAL',
                        'instructions_button': 'DECIMAL'}

        task_columns = {}
        for act in activities:
            if act.type == 'experiment':
                columns_aux = act.get_task_ids()
                columns_aux = {f'{name}_button': 'DECIMAL' for name in columns_aux}
                task_columns = {**task_columns, **columns_aux}
            elif act.type == 'questionnaire':
                task_columns[f'act{act.order}_button'] = 'DECIMAL'
        columns = {**base_columns, **task_columns}
        self._create_table("Timestamp", columns)


    def create_database_tables(self, 
                               screening_questions_db_columns,
                               activities_db_columns,
                               activity_pages):
        self.screening_columns = screening_questions_db_columns
        self.activities_columns = activities_db_columns
        self._create_response_table()
        self._create_quotas_table()
        self._create_experimental_tables(activity_pages)
        self._create_task_set_table(activity_pages)
        self._create_timestamp_table(activity_pages)


    def _populate_experimental_and_task_set_tables(self):
        designs = []
        for exp in self.experimental_activities:
            exp_type = self.experimental_activities[exp].experiment_type
            mode = self.experimental_activities[exp].settings_experimental_design_mode
            path = self.experimental_activities[exp].get_settings_builder_path()

            if mode == 'random':
                if exp_type == 'stated_choice':
                    fgen = scgen(self.experimental_activities[exp])
                elif exp_type == 'similarity_judgment':
                    fgen = sjgen(self.experimental_activities[exp])
                elif exp_type == 'likert_scale':
                    fgen = lsgen(self.experimental_activities[exp])
                df_exp = fgen.generate_random_experimental_design_csv(export=False)

            elif mode == 'custom':
                df_exp = pd.read_csv(path)

            # Populating Task_set table
            designs.append(df_exp[['task_id', 'set_id']].copy())
            designs[-1]['task_number'] = designs[-1].groupby('set_id').cumcount() + 1
            designs[-1] = designs[-1].pivot(index='set_id', columns='task_number', values='task_id')
            designs[-1].columns = self.experimental_activities[exp].get_task_ids()
            designs[-1].reset_index(inplace=True)

            # Populating Act Task tables
            df_exp.drop(columns=['set_id'], inplace=True)
            cols = [c for c in df_exp.columns if c != 'task_id']
            if cols:
                df_exp[cols] = df_exp[cols].astype(str)

            conn = sql.connect(self.database_path)
            df_exp.to_sql(exp, conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()

        # Combine designs based on set_id
        ds = pd.concat([df.set_index('set_id') for df in designs], axis=1, sort=True).reset_index()
        ds['used'] = 0
        conn = sql.connect(self.database_path)
        ds.to_sql('Task_set', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
 

    def _populate_quotas_table(self, survey_data):
        quota_gen = qgen(survey_data)

        if survey_data.screening_quotas_method == 'no_limit':
            df_quotas = quota_gen.generate_no_limit_quotas_csv(export=False)
        elif survey_data.screening_quotas_method == 'uniform':
            df_quotas = quota_gen.generate_uniform_quotas_csv(export=False)
        elif survey_data.screening_quotas_method == 'custom':
            df_quotas = quota_gen.generate_custom_quotas_csv(export=False)

        conn = sql.connect(self.database_path)
        df_quotas.to_sql('Quotas', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()

    def populate_database_tables(self, survey_data):
        self._populate_experimental_and_task_set_tables()
        self._populate_quotas_table(survey_data)