import streamlit as st
import sqlite3
import pandas as pd
from rubrics_db import create_tables, create_connection

# Setup
create_tables()

st.title("📝 Rubrics Management System")

# Page selector
page = st.sidebar.selectbox("Select Page", ["Add Rubric", "Add Student", "Add Scores", "View Reports"])

conn = create_connection()
c = conn.cursor()

if page == "Add Rubric":
    st.header("Add New Rubric")
    title = st.text_input("Rubric Title")
    description = st.text_area("Rubric Description")

    if st.button("Create Rubric"):
        c.execute("INSERT INTO Rubric (title, description) VALUES (?, ?)", (title, description))
        conn.commit()
        st.success("Rubric created.")

elif page == "Add Student":
    st.header("Add Student")
    name = st.text_input("Student Name")
    email = st.text_input("Student Email")
    
    if st.button("Add Student"):
        c.execute("INSERT INTO Student (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        st.success("Student added.")

elif page == "Add Scores":
    st.header("Add Scores for Assessment")
    assessments = c.execute("SELECT * FROM Assessment").fetchall()
    students = c.execute("SELECT * FROM Student").fetchall()

    assessment = st.selectbox("Assessment", assessments, format_func=lambda x: x[2])
    student = st.selectbox("Student", students, format_func=lambda x: x[1])

    criteria = c.execute("SELECT * FROM Criterion WHERE rubric_id = ?", (assessment[1],)).fetchall()
    
    for crit in criteria:
        levels = c.execute("SELECT * FROM Level WHERE criterion_id = ?", (crit[0],)).fetchall()
        level = st.selectbox(f"{crit[2]}", levels, format_func=lambda x: f"{x[2]} ({x[3]})", key=f"{crit[0]}")
        score = level[3]
        if st.button(f"Submit {crit[2]} Score", key=f"submit_{crit[0]}"):
            c.execute("""
            INSERT INTO Score (assessment_id, student_id, criterion_id, level_id, awarded_score)
            VALUES (?, ?, ?, ?, ?)""", (assessment[0], student[0], crit[0], level[0], score))
            conn.commit()
            st.success(f"{crit[2]} score submitted.")

elif page == "View Reports":
    st.header("Student Score Reports")
    students = c.execute("SELECT * FROM Student").fetchall()
    student = st.selectbox("Select Student", students, format_func=lambda x: x[1])

    query = """
    SELECT A.title, C.description, L.level_name, S.awarded_score
    FROM Score S
    JOIN Assessment A ON S.assessment_id = A.assessment_id
    JOIN Criterion C ON S.criterion_id = C.criterion_id
    JOIN Level L ON S.level_id = L.level_id
    WHERE S.student_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(student[0],))
    st.dataframe(df)

conn.close()
