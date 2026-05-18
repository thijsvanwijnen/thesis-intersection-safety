import sqlite3

conn = sqlite3.connect('surveys/survey-intersection-safety/database.db')
rows = conn.execute("""
    SELECT
        datetime(t.consent_button, 'unixepoch', '+2 hours') AS started_amsterdam,
        datetime(t.act2_button, 'unixepoch', '+2 hours') AS finished_amsterdam,
        CAST((t.act2_button - t.consent_button) / 60 AS INT) AS duration_minutes
    FROM Response r
    JOIN Timestamp t ON r.respondent_id = t.respondent_id
    WHERE r.act2_q1 IS NOT NULL
    ORDER BY t.consent_button DESC
    LIMIT 10
""").fetchall()

for r in rows:
    print(r)

conn.close()
