import sqlite3 as sql
from random import randint
import time

class Database:

    def __init__(self, path:str = 'database.db', date_user_id = time.mktime((2026, 5, 1, 0, 0, 0, 0, 0, 0))):
        """Initialize database connection."""
        self.path = path
        self.date_user_id = date_user_id

    
    def _write(self, query:str):
        """Write a query to database."""
        for _ in range(10):
            try:
                with sql.connect(self.path) as conn:
                    cursor = conn.cursor()
                    if query.startswith('BEGIN TRANSACTION'):
                        cursor.executescript(query)
                    else:
                        cursor.execute(query)
                    conn.commit()
                break 
            except sql.OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)  
                else:
                    raise


    def _write_human_inputs(self, query, params):
        """Write a query to database."""
        for _ in range(10):
            try:
                with sql.connect(self.path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                break 
            except sql.OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)  
                else:
                    raise


    def _read(self, query:str):
        """Read information from using query from database."""
        for _ in range(10):
            try:
                with sql.connect(self.path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    response = cursor.fetchall()
                return response

            except sql.OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)
                else:
                    raise
    

    def _read_with_params(self, query:str, params):
        """Read information from using query from database."""
        for _ in range(10):
            try:
                with sql.connect(self.path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    response = cursor.fetchall()
                return response

            except sql.OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)
                else:
                    raise
    

    def _get_new_respondent_id(self):
        """Get the next available respondent id."""
        currenttime = time.time()
        ref_time = currenttime - self.date_user_id
        return int(ref_time*1000)
    

    def _get_next_task_set_id(self):
        """Get the next available task set id."""
        query = "SELECT MIN(set_id) FROM Task_set WHERE used = 0"
        return self._read(query)[0][0]
    

    def create_new_respondent(self, unix_time:float):
        """Create a new respondent and return the respondent id and task set id."""
        respondent_id = self._get_new_respondent_id()
        set_id = self._get_next_task_set_id()

        query = f"""BEGIN TRANSACTION;
                    INSERT INTO Response (respondent_id, set_id) VALUES ({respondent_id}, {set_id});
                    INSERT INTO Timestamp (respondent_id, consent_button) VALUES ({respondent_id}, {unix_time});
                    UPDATE Task_set SET used = 1 WHERE set_id = {set_id};
                    COMMIT;
                    """
        
        self._write(query)
        
        return respondent_id


    def create_new_respondent_with_external_id(self, external_id:str, unix_time:float):
        respondent_id = self._get_new_respondent_id()
        set_id = self._get_next_task_set_id()

        query = f"""BEGIN TRANSACTION;
                    INSERT INTO Response (respondent_id, set_id, external_id) VALUES ({respondent_id}, {set_id}, "{external_id}");
                    INSERT INTO Timestamp (respondent_id, consent_button) VALUES ({respondent_id}, {unix_time});
                    UPDATE Task_set SET used = 1 WHERE set_id = {set_id};
                    COMMIT;
                    """
        self._write(query)
        
        return respondent_id


    def register_screening_responses(self, respondent_id:int, responses:dict):
        """Update the screening responses from respondent."""
        query = "UPDATE Response SET sq1_professional_role = ?, sq2_years_experience = ?, sq3_intersection_assessment_experience = ? WHERE respondent_id = ?"
        params = tuple(responses[col] for col in responses) + (respondent_id,)
        self._write_human_inputs(query, params)


    def register_questionnaire_responses(self, respondent_id:int, activity_key:str, responses:dict):
        """Update the questionnaire responses from respondent."""
        n_questions = len(responses)
        set_clause = ', '.join([f"{activity_key}_q{i+1} = ?" for i in range(n_questions)])
        query = f"UPDATE Response SET {set_clause} WHERE respondent_id = ?"
        params = tuple(responses[col] for col in responses) + (respondent_id,)
        self._write_human_inputs(query, params)

  
    def _get_data_for_task(self, respondent_id:int, activity_key:str, task_number:int):
        """Get the data for a given task."""
        query = lambda activity_key, task_number: f"""SELECT * 
                    FROM {activity_key.capitalize()}_task
                   WHERE task_id = (SELECT {activity_key}_task_{task_number} 
                                      FROM Task_set 
                                      WHERE set_id = (SELECT set_id FROM Response WHERE respondent_id = ?))"""
        params = (respondent_id,)
        return self._read_with_params(query(activity_key, task_number), params)[0][1:]


    def get_data_for_respondent(self, respondent_id:int, n_tasks_per_activity:dict):
        """Get the data for a given respondent."""
        tasks = {}
        for activity_key in n_tasks_per_activity:
            for task_number in range(1, n_tasks_per_activity[activity_key]+1):
                tasks[f"{activity_key}_task_{task_number}"] = self._get_data_for_task(respondent_id, activity_key, task_number)
        return tasks
    

    def register_experiment_response(self, respondent_id:int, activity_key:str, task_number:int, response:str):
        """Register the response of a respondent for a task."""
        query = lambda activity_key, task_number: f"UPDATE Response SET {activity_key}_t{task_number} = ? WHERE respondent_id = ?"
        params = (response, respondent_id)
        self._write_human_inputs(query(activity_key, task_number), params)

    
    def register_time(self, respondent_id:int, button_id:str, time:float):
        """Register the time of a respondent."""
        button_id = button_id.replace('-','_')
        query = f"""UPDATE Timestamp SET {button_id} = '{time}' WHERE respondent_id = {respondent_id}"""
        self._write(query)


    def allows_respondent_to_continue(self, responses:dict):
        """Check if quotas allow continuing for given screening responses."""
        query = "SELECT quota - actual FROM Quotas WHERE sq1_professional_role = ? AND sq2_years_experience = ? AND sq3_intersection_assessment_experience = ?"
        params = tuple(responses[col] for col in responses)
        quota = self._read_with_params(query, params)
        return quota[0][0] > 0


    def update_quota(self, respondent_id):
        """Register one extra response for the screening questions set in Quotas"""

        # Check sq responses from respondent
        query_sq_responses = "SELECT sq1_professional_role, sq2_years_experience, sq3_intersection_assessment_experience FROM Response WHERE respondent_id = ?"
        params = (respondent_id,)
        responses = self._read_with_params(query_sq_responses, params)

        # Update quota for those responses
        query_quotas = "UPDATE Quotas SET actual = actual + 1 WHERE sq1_professional_role = ? AND sq2_years_experience = ? AND sq3_intersection_assessment_experience = ?"
        params = (responses[0])
        self._write_human_inputs(query_quotas, params)