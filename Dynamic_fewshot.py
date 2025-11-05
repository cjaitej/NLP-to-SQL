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

# --- SQL query generation ---
def generate_sql(schema, prompt, question, top_4):
    model = genai.GenerativeModel("gemini-2.5-flash")
    final_prompt = prompt.format(db_schema=schema, user_question=question, top_4=top_4)

    try:
        response = model.generate_content(final_prompt)
        cleaned_query = response.text.strip().replace("```sql", "").replace("```", "")
        return cleaned_query

    except ValueError:
        print("  - API Error: Response was blocked by the safety filter.")
        return ""
    except Exception as e:
        print(f"  - Unexpected API error: {e}")
        return ""

# --- Execute Query ---
def execute_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return sorted(results)
    except Exception:
        return None

def main():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=API_KEY)

    data_set = input("Enter dataset to start (spider/bird): ").strip()

    good_prompt = """You are an expert data scientist and SQL engineer.
You are given a database schema and a natural language question.
Your task is to carefully analyze the schema, reason about table relationships,
and generate a correct and efficient SQL query that fully answers the question.
Also be careful to only output valid SQL, no English text.

Database Engine:
SQLite

Few-shot examples:
{top_4}

Now do the same for:

Database Schema:
{db_schema}

Question:
{user_question}

-- Reasoning
(2–6 lines)

-- SQL Query
"""

    # ✅ Dataset file
    sub_path = (
        os.path.join("spider", "dev_spider_filtered.json")
        if data_set == "spider"
        else os.path.join("data", "bird", "dev_bird_filtered.json")
    )

    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    correct = 0
    total_len = len(dev_data)
    data_log = []

    print(f"--- Starting Execution Accuracy evaluation on {total_len} examples ---")

    for i, item in enumerate(dev_data):
        db_id = item["db_id"]
        question = item["question"]
        orig_query = item["query"] if data_set == "spider" else item["SQL"]
        top_4 = item["top_5"][:4]

        # ✅ DB path
        path = (
            os.path.join("spider", "database", db_id, f"{db_id}.sqlite")
            if data_set == "spider"
            else os.path.join("data", "bird", "dev_databases", db_id, f"{db_id}.sqlite")
        )

        schema = get_schema(path)

        # ✅ SAFE SQL extraction
        llm_output = generate_sql(schema, good_prompt, question, top_4)

        if "-- SQL Query" in llm_output:
            pred_query = llm_output.split("-- SQL Query")[-1].strip()
        else:
            pred_query = llm_output.strip()

        pred_query = pred_query.replace("```sql", "").replace("```", "").strip()

        pred_result = execute_query(path, pred_query)
        orig_result = execute_query(path, orig_query)

        print(f"\n[{i+1}/{total_len}] Question: {question}")
        print("Generated SQL:", pred_query)

        if pred_result is not None and pred_result == orig_result:
            correct += 1
            data_log.append(pred_query + " ✅")
            print("✅ MATCH")
        else:
            data_log.append(pred_query + " ❌")
            print("❌ WRONG")

        print("Correct so far:", correct)
        time.sleep(10)

    # ✅ Save results
    os.makedirs("results", exist_ok=True)
    out_file = f"results/results_{data_set}.json"
    with open(out_file, "w") as f:
        json.dump(data_log, f, indent=4)

    accuracy = (correct / total_len) * 100 if total_len > 0 else 0
    print("\n--- Evaluation Complete ✅ ---")
    print(f"Execution Accuracy: {accuracy:.2f}%")
    print(f"Saved log to: {out_file}")

if __name__ == "__main__":
    main()
