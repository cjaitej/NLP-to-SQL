from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai
question=input("enter text query")
prompt = """
You are an expert in converting English questions to SQL queries!
The SQL database name is STUDENT and has the following columns: NAME, CLASS, SECTION.

Examples:
Q: How many entries of records are present?
A: SELECT COUNT(*) FROM STUDENT;

Q: Tell me all the students studying in Data Science class.
A: SELECT * FROM STUDENT WHERE CLASS = "Data Science";

Return only valid SQL code — no ``` or 'sql' tags.
"""
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model=genai.GenerativeModel("gemini-2.5-flash")
response=model.generate_content([prompt,question])
print(response.text)