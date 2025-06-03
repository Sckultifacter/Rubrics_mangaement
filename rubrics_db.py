import sqlite3

DB_NAME = "rubrics.db"

def create_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def create_tables():
    conn = create_connection()
    c = conn.cursor()

    # Rubric table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Rubric (
        rubric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT
    )
    """)

    # Student table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Student (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Assessment table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Assessment (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rubric_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        due_date TEXT,
        FOREIGN KEY (rubric_id) REFERENCES Rubric (rubric_id)
    )
    """)

    # Criterion table (criteria under each rubric)
    c.execute("""
    CREATE TABLE IF NOT EXISTS Criterion (
        criterion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rubric_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        FOREIGN KEY (rubric_id) REFERENCES Rubric (rubric_id)
    )
    """)

    # Level table (levels for each criterion, e.g., Excellent, Good, etc.)
    c.execute("""
    CREATE TABLE IF NOT EXISTS Level (
        level_id INTEGER PRIMARY KEY AUTOINCREMENT,
        criterion_id INTEGER NOT NULL,
        level_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        FOREIGN KEY (criterion_id) REFERENCES Criterion (criterion_id)
    )
    """)

    # Score table (scores assigned to students per assessment criterion and level)
    c.execute("""
    CREATE TABLE IF NOT EXISTS Score (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        criterion_id INTEGER NOT NULL,
        level_id INTEGER NOT NULL,
        awarded_score INTEGER NOT NULL,
        FOREIGN KEY (assessment_id) REFERENCES Assessment (assessment_id),
        FOREIGN KEY (student_id) REFERENCES Student (student_id),
        FOREIGN KEY (criterion_id) REFERENCES Criterion (criterion_id),
        FOREIGN KEY (level_id) REFERENCES Level (level_id)
    )
    """)

    conn.commit()
    conn.close()
