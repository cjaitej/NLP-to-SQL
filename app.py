# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# # Load your API key from a .env file
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# # Configure the API key once at the start
# if not api_key:
#     raise ValueError("API key not found. Please set it in your .env file.")
# genai.configure(api_key=api_key)

# # The rewritten function from above
# def generate_sql_query(user_query: str, prompt_template: str) -> str:
#     model = genai.GenerativeModel("gemini-pro")
#     full_prompt = f"{prompt_template}\n\nEnglish Question: {user_query}\nSQL Query:"
#     response = model.generate_content(full_prompt)
#     return response.text.strip()

# # Main execution block
# if __name__ == "__main__":
#     # Your prompt template as a simple string
#     sql_prompt_template = """You are an expert in converting English questions to SQL query!
# The SQL database has the name STUDENT and has the following columns - NAME, CLASS, SECTION.

# For example:
# - English: "How many entries of records are present?"
#   SQL: SELECT COUNT(*) FROM STUDENT;
# - English: "Tell me all the students studying in Data Science class?"
#   SQL: SELECT * FROM STUDENT where CLASS="Data Science";

# Do not include ``` in the beginning or end of your response."""

#     # Get input from the user
#     user_question = input("Enter your English query for the STUDENT database: ")
    
#     # Call the function to get the result
#     sql_result = generate_sql_query(user_question, sql_prompt_template)
    
#     # Print the final result
#     print("\nGenerated SQL:")
#     print(sql_result)





from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# ---------------------------
# 1️⃣ Load environment variables
# ---------------------------
load_dotenv()  # Loads .env file containing GOOGLE_API_KEY

# ---------------------------
# 2️⃣ Configure Gemini API key
# ---------------------------
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------------------------
# 3️⃣ Function: Get Gemini Response
# ---------------------------
def get_gemini_response(question, prompt):
    """
    Uses Gemini to convert natural language question into an SQL query.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
  # ✅ Correct model name
        response = model.generate_content([prompt, question])
        sql_query = response.text.strip()

        # Clean any code formatting if present
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        return f"⚠️ Error generating SQL: {str(e)}"

# ---------------------------
# 4️⃣ Function: Run SQL query
# ---------------------------
def read_sql_query(sql, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return [f"⚠️ Error executing SQL: {str(e)}"]

# ---------------------------
# 5️⃣ Define prompt for Gemini
# ---------------------------
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

# ---------------------------
# 6️⃣ Streamlit UI
# ---------------------------
st.set_page_config(page_title="Gemini SQL Query App")
st.title("💡 Gemini-Powered SQL Query Generator")
st.write("Ask me anything about the STUDENT database!")

question = st.text_input("Enter your question:")

if st.button("Ask Gemini"):
    if not question.strip():
        st.warning("Please enter a question first.")
        st.stop()

    # Step 1: Get SQL from Gemini
    sql_query = get_gemini_response(question, prompt)
    st.subheader("🧠 Generated SQL Query")
    st.code(sql_query, language="sql")

    # Step 2: Execute SQL on student.db
    rows = read_sql_query(sql_query, "student.db")

    # Step 3: Display results
    st.subheader("📊 Query Results")
    if not rows:
        st.info("No results found or invalid query.")
    else:
        for row in rows:
            st.write(row)

