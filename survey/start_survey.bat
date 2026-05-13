@echo off
set PYTHONPATH=%PYTHONPATH%;C:\Users\Thijs\OneDrive\Documents\Studie\EPA\Second_year\Afstuderen\Project\core-usage\pixelsurvey-core
call C:\Projects\envs\psenv\Scripts\activate
cd C:\Users\Thijs\OneDrive\Documents\Studie\EPA\Second_year\Afstuderen\Project\core-usage
python pixelsurvey-core\survey_gen.py intersection-safety
cd surveys\survey-intersection-safety
start chrome http://127.0.0.1:8050
python app.py
