import sqlite3 as sql
from pathlib import Path

import vars as v

class QueriesGenerator:
    def __init__(self, survey_id):
        self.database_path = Path(f"{v.SURVEYS_DIR}/survey-{survey_id}/database.db")
    

    def _read(self, query:str):
        """Read information from using query from database."""
        with sql.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            response = cursor.fetchall()
        return response


    def _read_column_names_from_table(self, table_name:str, keep: str = None):
        """Read the column names from a database table.
        keep: Optional prefix to filter column names. ['sq', 'act', 'actN']
        """
        query = f"PRAGMA table_info({table_name})"
        columns = self._read(query)
        if keep:
            return [column[1] for column in columns if keep in column[1].split('_')[0]]
        return [column[1] for column in columns]
    

    def gen_screening_write_query(self):
        columns = self._read_column_names_from_table('Response', keep='sq')
        set_clause = ', '.join([f"{col} = ?" for col in columns])
        query = f"UPDATE Response SET {set_clause} WHERE respondent_id = ?"
        return query


    def gen_quotas_read_query(self):
        columns = self._read_column_names_from_table('Response', keep='sq')
        where_clause = ' AND '.join([f"{col} = ?" for col in columns])
        query = f"SELECT quota - actual FROM Quotas WHERE {where_clause}"
        return query
    

    def gen_quotas_write_query(self):
        columns = self._read_column_names_from_table('Response', keep='sq')
        where_clause = ' AND '.join([f"{col} = ?" for col in columns])
        query = f"UPDATE Quotas SET actual = actual + 1 WHERE {where_clause}"
        return query
    

    def gen_screening_read_query(self):
        columns = self._read_column_names_from_table('Response', keep='sq')
        select_clause = ', '.join([f"{col}" for col in columns])
        query = f"SELECT {select_clause} FROM Response WHERE respondent_id = ?"
        return query