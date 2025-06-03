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
