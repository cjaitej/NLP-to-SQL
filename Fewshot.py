import sqlite3
import json
from dotenv import load_dotenv
import google.generativeai as genai
import os
import time

# --- Getting schema (no changes needed) ---
def get_schema(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = "\n".join([row[0] for row in cursor.fetchall()])
    conn.close()
    return schema

# --- SQL query generation (with model name fix) ---
def generate_sql(schema, prompt, question):
    """
    Generates a SQL query using the Gemini model with robust error handling.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    final_prompt = prompt.format(db_schema=schema, user_question=question)
    
    try:
        response = model.generate_content(final_prompt)
        
        # The library raises a ValueError if the response is blocked.
        # This is the most reliable way to check for a safety block.
        cleaned_query = response.text.strip().replace("```sql", "").replace("```", "")
        return cleaned_query
        
    except ValueError:
        # This specific error indicates a safety filter block.
        print("  - API Error: Response was blocked by the safety filter.")
        # You can uncomment the line below to see the specific block reason.
        # print(f"  - Prompt Feedback: {response.prompt_feedback}")
        return "" # Return empty string on block
        
    except Exception as e:
        # This will catch other errors, like connection issues.
        print(f"  - An unexpected API error occurred: {e}")
        return "" # Return empty string on other errors

# --- Execution accuracy (CRITICAL FIX) ---
def execute_query(db_path, query):
    """Executes a query and returns sorted results or None on error."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        # CORRECTED: You must fetch the results!
        results = cursor.fetchall()
        conn.close()
        # Sorting is important for a reliable comparison
        return sorted(results)
    except Exception:
        # Return None if the SQL query has an error and cannot be executed
        return None

def main():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=API_KEY)
    data_set=input("enter dataset to start")
    good_prompt="""You are an expert data scientist and SQL engineer. You are given a database schema and a natural language question. Your task is to carefully analyze the schema, reason about table relationships, and generate a correct and efficient SQLite query that fully answers the question.

Database Engine:
SQLite

Follow the reasoning and query structure as shown in the few-shot examples below.

Example 1:
-- Question
Find the names of all students majoring in 'Computer Science'.

-- Reasoning
We need student names and their corresponding major. Join `students` with `majors` on `major_id`, then filter for major_name = 'Computer Science'.

-- SQL Query
```sql
SELECT s.name
FROM students AS s
JOIN majors AS m ON s.major_id = m.major_id
WHERE m.major_name = 'Computer Science';

Example 2:
-- Schema
-- Question
Find the average salary for each department.

-- Reasoning
We group employees by department and compute the average salary for each group.

-- SQL Query

SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;

Example 3:
-- Question
List the names of customers who placed more than 3 orders.

-- Reasoning
We join customers with orders, group by customer, and count their orders. Filter those with count > 3.

-- SQL Query

SELECT c.customer_name
FROM customers AS c
JOIN orders AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
HAVING COUNT(o.order_id) > 3;

Example 4:
-- Question
Find the top 3 highest-rated movies released after 2015.

-- Reasoning
We filter movies by release_year > 2015, order them by rating descending, and limit to 3 results.

-- SQL Query

SELECT title, rating
FROM movies
WHERE release_year > 2015
ORDER BY rating DESC
LIMIT 3;

Example 5:
-- Question
Find the total sales revenue (price * quantity) for each product.

-- Reasoning
Join products with sales on product_id, multiply price by quantity, then group by product name to sum the revenue.

-- SQL Query

SELECT p.name, SUM(p.price * s.quantity) AS total_revenue
FROM products AS p
JOIN sales AS s ON p.product_id = s.product_id
GROUP BY p.name;

Now, for the following schema and question, follow the same reasoning process and output format:

Database Schema:
{db_schema}

Question:
{user_question}

-- Reasoning
(Concise 2–6 line logical explanation describing how you derived the query)

-- SQL Query

SELECT ...
FROM ...
WHERE ...
"""

    
    sub_path = (
    os.path.join("spider", "dev_subset.json")
    if data_set == "spider"
    else os.path.join("data", "bird", "dev_subset.json")
)


    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    correct = 0
    # CORRECTED: Loop and total length must match
    data_to_evaluate = dev_data # Let's test on 5 examples
    total_len = len(data_to_evaluate)
    
    print(f"--- Starting Execution Accuracy evaluation on {total_len} examples ---")
    data=[]
    for i, item in enumerate(data_to_evaluate):
        db_id = item["db_id"]
        question = item["question"]
        orig_query = item["query"] if data_set == "spider" else item["SQL"]

        
        # This is the correct path to the DATABASE file
        path = (
    os.path.join("spider", "database", db_id, f"{db_id}.sqlite")
    if data_set == "spider"
    else os.path.join("data", "bird", "dev_databases", db_id, f"{db_id}.sqlite")
)

        
        schema = get_schema(path)
        pred_query = generate_sql(schema, good_prompt, question).split('-- SQL Query')[1]

        # --- CORRECTED EXECUTION LOGIC ---
        # Use the correct database path for both queries
        pred_result = execute_query(path, pred_query)
        orig_result = execute_query(path, orig_query)

        print(f"\n--- Processing Example {i+1}/{total_len} ---")
        print(f"Question: {question}")
        print(f"  - Generated SQL: {pred_query}")
        
        # Compare the RESULTS, not the cursor objects
        if pred_result is not None and pred_result == orig_result:
            correct += 1
            data.append(f"{pred_query}"+"✅")
            print("  - Result: ✅ Correct (Execution Match)")
        else:
            data.append(f"{pred_query}"+"❌")
            print("  - Result: ❌ Incorrect (Execution Mismatch or Error)")
        time.sleep(10)
    file_path_data=os.path.join("spider","results.json")
    with open(file_path_data,'w') as f:
        json.dump(data,f,indent=4)
         # Respect API rate limits

    accuracy = (correct / total_len) * 100 if total_len > 0 else 0
    print("\n--- Evaluation Complete ---")
    print(f"Execution Accuracy on {total_len} examples is: {accuracy:.2f}%")

if __name__ == "__main__":
    main()