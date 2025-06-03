import sqlite3

def create_connection():
    return sqlite3.connect("rubrics.db")

def create_tables():
    conn = create_connection()
    c = conn.cursor()
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS Rubric (
        rubric_id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS Criterion (
        criterion_id INTEGER PRIMARY KEY,
        rubric_id INTEGER,
        description TEXT,
        FOREIGN KEY (rubric_id) REFERENCES Rubric(rubric_id)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS Level (
        level_id INTEGER PRIMARY KEY,
        criterion_id INTEGER,
        level_name TEXT,
        score INTEGER,
        FOREIGN KEY (criterion_id) REFERENCES Criterion(criterion_id)
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS Student (
        student_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS Assessment (
        assessment_id INTEGER PRIMARY KEY,
        rubric_id INTEGER,
        title TEXT,
        due_date DATE,
        FOREIGN KEY (rubric_id) REFERENCES Rubric(rubric_id)
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS Score (
        score_id INTEGER PRIMARY KEY,
        assessment_id INTEGER,
        student_id INTEGER,
        criterion_id INTEGER,
        level_id INTEGER,
        awarded_score INTEGER,
        FOREIGN KEY (assessment_id) REFERENCES Assessment(assessment_id),
        FOREIGN KEY (student_id) REFERENCES Student(student_id),
        FOREIGN KEY (criterion_id) REFERENCES Criterion(criterion_id),
        FOREIGN KEY (level_id) REFERENCES Level(level_id)
    )""")

    conn.commit()
    conn.close()
