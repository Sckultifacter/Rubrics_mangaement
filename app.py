import streamlit as st
import sqlite3
import pandas as pd
from rubrics_db import create_tables, create_connection

# Initialize DB
create_tables()
conn = create_connection()
c = conn.cursor()

st.title("📝 Rubrics Management System")

# Sidebar navigation
page = st.sidebar.selectbox("Choose Action", ["Add Rubric", "Add Student", "Add Scores", "View Reports"])

# ------------------ PAGE 1: Add Rubric ------------------
if page == "Add Rubric":
    st.header("Add New Rubric")
    title = st.text_input("Rubric Title")
    description = st.text_area("Description")

    if st.button("Create Rubric"):
        if title:
            c.execute("INSERT INTO Rubric (title, description) VALUES (?, ?)", (title, description))
            conn.commit()
            st.success("Rubric added.")
        else:
            st.error("Rubric title is required.")

# ------------------ PAGE 2: Add Student ------------------
elif page == "Add Student":
    st.header("Add Student")
    name = st.text_input("Student Name")
    email = st.text_input("Student Email")

    if st.button("Add Student"):
        if name and email:
            c.execute("INSERT INTO Student (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            st.success("Student added.")
        else:
            st.error("Both name and email are required.")

# ------------------ PAGE 3: Add Scores ------------------
elif page == "Add Scores":
    st.header("Enter Scores")

    assessments = c.execute("SELECT * FROM Assessment").fetchall()
    if not assessments:
        st.warning("No assessments found. Please create an assessment directly in the database.")
    else:
        assessment = st.selectbox("Assessment", assessments, format_func=lambda x: x[2])

        students = c.execute("SELECT * FROM Student").fetchall()
        if not students:
            st.warning("No students found. Add students first.")
        else:
            student = st.selectbox("Student", students, format_func=lambda x: x[1])

            if assessment and student:
                criteria = c.execute("SELECT * FROM Criterion WHERE rubric_id = ?", (assessment[1],)).fetchall()
                if not criteria:
                    st.warning("No criteria found for this rubric.")
                else:
                    for crit in criteria:
                        levels = c.execute("SELECT * FROM Level WHERE criterion_id = ?", (crit[0],)).fetchall()
                        level = st.selectbox(f"{crit[2]}", levels, format_func=lambda x: f"{x[2]} ({x[3]})", key=f"{crit[0]}")
                        score = level[3]
                        if st.button(f"Submit {crit[2]} Score", key=f"submit_{crit[0]}"):
                            c.execute("""
                                INSERT INTO Score (assessment_id, student_id, criterion_id, level_id, awarded_score)
                                VALUES (?, ?, ?, ?, ?)""", 
                                (assessment[0], student[0], crit[0], level[0], score))
                            conn.commit()
                            st.success(f"Score for '{crit[2]}' added.")

# ------------------ PAGE 4: View Reports ------------------
elif page == "View Reports":
    st.header("Student Report Viewer")

    students = c.execute("SELECT * FROM Student").fetchall()
    if not students:
        st.info("No students available.")
    else:
        student = st.selectbox("Choose Student", students, format_func=lambda x: x[1])
        query = """
        SELECT A.title AS Assessment, C.description AS Criterion, L.level_name AS Level, S.awarded_score AS Score
        FROM Score S
        JOIN Assessment A ON S.assessment_id = A.assessment_id
        JOIN Criterion C ON S.criterion_id = C.criterion_id
        JOIN Level L ON S.level_id = L.level_id
        WHERE S.student_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(student[0],))
        if df.empty:
            st.info("No scores found for this student.")
        else:
            st.dataframe(df)

conn.close()
