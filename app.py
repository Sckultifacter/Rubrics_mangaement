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
page = st.sidebar.selectbox("Choose Action", [
    "Add Rubric",
    "Add Criterion",
    "Add Level",
    "Add Student",
    "Add Assessment",
    "Add Scores",
    "View Reports"
])

# ------------------ Add Rubric ------------------
if page == "Add Rubric":
    st.header("Add New Rubric")
    title = st.text_input("Rubric Title")
    description = st.text_area("Description")

    if st.button("Create Rubric"):
        if title:
            c.execute("INSERT INTO Rubric (title, description) VALUES (?, ?)", (title, description))
            conn.commit()
            st.success("Rubric added.")

# ------------------ Add Criterion ------------------
elif page == "Add Criterion":
    st.header("Add Criterion to Rubric")
    rubrics = c.execute("SELECT * FROM Rubric").fetchall()
    if not rubrics:
        st.warning("No rubrics available. Please add a rubric first.")
    else:
        rubric = st.selectbox("Select Rubric", rubrics, format_func=lambda x: x[1])
        description = st.text_input("Criterion Description")
        if st.button("Add Criterion"):
            if description:
                c.execute("INSERT INTO Criterion (rubric_id, description) VALUES (?, ?)", (rubric[0], description))
                conn.commit()
                st.success(f"Criterion added to '{rubric[1]}' rubric.")
            else:
                st.error("Criterion description cannot be empty.")

# ------------------ Add Level ------------------
elif page == "Add Level":
    st.header("Add Level to Criterion")
    criteria = c.execute("""
        SELECT Criterion.criterion_id, Rubric.title, Criterion.description 
        FROM Criterion JOIN Rubric ON Criterion.rubric_id = Rubric.rubric_id
    """).fetchall()

    if not criteria:
        st.warning("No criteria available. Please add criteria first.")
    else:
        crit = st.selectbox("Select Criterion", criteria, format_func=lambda x: f"{x[1]} - {x[2]}")
        level_name = st.text_input("Level Name (e.g., Excellent, Good)")
        score = st.number_input("Representative Score", min_value=0, step=1)
        min_score = st.number_input("Minimum Score", min_value=0, step=1)
        max_score = st.number_input("Maximum Score", min_value=0, step=1)

        if st.button("Add Level"):
            if level_name and score >= 0:
                c.execute(
                    "INSERT INTO Level (criterion_id, level_name, score, min_score, max_score) VALUES (?, ?, ?, ?, ?)",
                    (crit[0], level_name, score, min_score, max_score)
                )
                conn.commit()
                st.success(f"Level '{level_name}' added to criterion '{crit[2]}'.")
            else:
                st.error("Please provide valid level name and score range.")

# ------------------ Add Student ------------------
elif page == "Add Student":
    st.header("Add Student")
    name = st.text_input("Student Name")
    email = st.text_input("Student Email")

    if st.button("Add Student"):
        if name and email:
            c.execute("INSERT INTO Student (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            st.success("Student added.")

# ------------------ Add Assessment ------------------
elif page == "Add Assessment":
    st.header("Create New Assessment")
    rubrics = c.execute("SELECT * FROM Rubric").fetchall()

    if not rubrics:
        st.warning("No rubrics available. Please add a rubric first.")
    else:
        rubric = st.selectbox("Choose Rubric", rubrics, format_func=lambda x: x[1])
        title = st.text_input("Assessment Title")
        due_date = st.date_input("Due Date")

        if st.button("Create Assessment"):
            if title:
                c.execute("INSERT INTO Assessment (rubric_id, title, due_date) VALUES (?, ?, ?)",
                          (rubric[0], title, due_date))
                conn.commit()
                st.success("Assessment created successfully.")
            else:
                st.error("Assessment title is required.")

# ------------------ Add Scores ------------------
elif page == "Add Scores":
    st.header("Enter Scores")
    assessments = c.execute("SELECT * FROM Assessment").fetchall()
    if not assessments:
        st.warning("No assessments found. Please add one.")
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
                        if levels:
                            level = st.selectbox(
                                f"{crit[2]}", levels,
                                format_func=lambda x: f"{x[2]} (Score: {x[3]}, Range: {x[4]}-{x[5]})",
                                key=f"{crit[0]}"
                            )
                            score = level[3]
                            if st.button(f"Submit {crit[2]} Score", key=f"submit_{crit[0]}"):
                                c.execute("""
                                    INSERT INTO Score (assessment_id, student_id, criterion_id, level_id, awarded_score)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (assessment[0], student[0], crit[0], level[0], score))
                                conn.commit()
                                st.success(f"Score for '{crit[2]}' submitted.")

# ------------------ View Reports ------------------
elif page == "View Reports":
    st.header("Student Report Viewer")
    students = c.execute("SELECT * FROM Student").fetchall()
    if not students:
        st.info("No students available.")
    else:
        student = st.selectbox("Choose Student", students, format_func=lambda x: x[1])
        df = pd.read_sql_query("""
            SELECT A.title AS Assessment, C.description AS Criterion, L.level_name AS Level, 
                   L.min_score || '-' || L.max_score AS Range, S.awarded_score AS Score
            FROM Score S
            JOIN Assessment A ON S.assessment_id = A.assessment_id
            JOIN Criterion C ON S.criterion_id = C.criterion_id
            JOIN Level L ON S.level_id = L.level_id
            WHERE S.student_id = ?
        """, conn, params=(student[0],))

        if df.empty:
            st.info("No scores found for this student.")
        else:
            total_df = df.groupby("Assessment")["Score"].sum().reset_index(name="Total Score")
            st.subheader("Score Breakdown")
            st.dataframe(df)
            st.subheader("Total per Assessment")
            st.dataframe(total_df)

conn.close()
