import sqlite3
import google.generativeai as genai
import time
import re
import math
import os
import json
from dotenv import load_dotenv



def preprocessing():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=API_KEY)
    data_set = input("Enter dataset to start (spider/bird): ").strip()
    return data_set

def execute_query(db_path, query):
    """Executes a query and returns (sorted results, exec_time) or (None, None) on error."""
    try:
        start = time.time()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()
        exec_time = time.time() - start
        return sorted(results), exec_time
    except Exception:
        return None, None

def generate_sql(schema, prompt, question, topk=None):
    """
    Generates a SQL query using the Gemini model with robust error handling.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")

    if topk:
        final_prompt = prompt.format(db_schema=schema, user_question=question, top_k=topk)
    else:
        final_prompt = prompt.format(db_schema=schema, user_question=question)

    try:
        response = model.generate_content(final_prompt)
        cleaned_query = response.text.strip().replace("```sql", "").replace("```", "")
        return cleaned_query

    except ValueError:
        print("  - API Error: Response was blocked by the safety filter.")
        return "" 

    except Exception as e:
        print(f"  - An unexpected API error occurred: {e}")
        return "" 

def compute_ves(exec_results):
    num_queries = len(exec_results)
    if num_queries == 0:
        return 0
    total_ratio = 0
    for result in exec_results:
        ratio = result.get("time_ratio", 0)
        total_ratio += math.sqrt(ratio) * 100 if ratio != 0 else 0
    return total_ratio / num_queries

def get_schema(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = "\n".join([row[0] for row in cursor.fetchall()])
    conn.close()
    return schema

def evaluate(data_to_evaluate, good_prompt, data_set, version_name):
    correct = 0
    total_len = len(data_to_evaluate)
    print(f"--- Starting Execution Accuracy evaluation on {total_len} examples ---")
    data=[]
    for i, item in enumerate(data_to_evaluate):
        db_id = item["db_id"]
        question = item["question"]
        orig_query = item["query"] if data_set == "spider" else item["SQL"]


        
        path = os.path.join("spider", "database", db_id, f"{db_id}.sqlite") if data_set=="spider" else os.path.join("data","bird","dev_databases", db_id, f"{db_id}.sqlite")

        d = {}
        d["id"] = db_id
        d["question"] = question
        d["original_query"] = orig_query

        

        schema = get_schema(path)
        # print(schema)
        pred_query = generate_sql(schema, good_prompt, question)
        match =  re.search(r"SELECT[\s\S]*?;", pred_query, re.IGNORECASE)
        pred_query = match.group(0).strip() if match else None
        d["pred_query"] = pred_query

        pred_result, pred_time = execute_query(path, pred_query)
        orig_result, orig_time = execute_query(path, orig_query)


        if pred_time and orig_time and pred_time > 0:
            time_ratio = orig_time / pred_time
        else:
            time_ratio = 0

        
        d["pred_time"] = pred_time
        d["orig_time"] = orig_time
        d["time_ratio"] = time_ratio

        print(f"\n--- Processing Example {i+1}/{total_len} ---")
        print(f"Question: {question}")
        print(f"  - Generated SQL: {pred_query}")

        
        if pred_result is not None and pred_result == orig_result:
            correct += 1
            d["check"] = True
            print("  - Result: ✅ Correct (Execution Match)")
        else:
            d["check"] = False
            print("  - Result: ❌ Incorrect (Execution Mismatch or Error)")
        data.append(d)
        accuracy = (correct / (i + 1)) * 100 if total_len > 0 else 0
        print(f"Accuracy = {accuracy}")
        
        time.sleep(10)

    file_path_data=os.path.join("spider",f"results_{version_name}.json")
    with open(file_path_data,'w') as f:
        json.dump(data,f,indent=4)
         


    accuracy = (correct / (i + 1)) * 100 if total_len > 0 else 0
    ves = compute_ves(data)
    print("\n--- Evaluation Complete ---")
    print(f"Execution Accuracy on {i + 1} examples is: {accuracy:.2f}%")
    print(f"Valid Efficiency Score (VES): {ves:.2f}")

    summary_path = f"{version_name}.txt"
    with open(summary_path, "w") as f:
        f.write(f"Execution Accuracy: {accuracy:.2f}%\n")
        f.write(f"Valid Efficiency Score (VES): {ves:.2f}\n")

    print(f"Results saved as {summary_path}")
    return accuracy, ves


def evaluate_dynamic_fewshot(data_to_evaluate, good_prompt, top_k, data_set, version_name):
    correct = 0
    total_len = len(data_to_evaluate)
    print(f"--- Starting Execution Accuracy evaluation on {total_len} examples ---")
    data=[]
    for i, item in enumerate(data_to_evaluate):
        db_id = item["db_id"]
        question = item["question"]
        orig_query = item["query"] if data_set == "spider" else item["SQL"]
        topk = item["top_5"][:top_k]


        path = os.path.join("spider", "database", db_id, f"{db_id}.sqlite") if data_set=="spider" else os.path.join("data","bird","dev_databases", db_id, f"{db_id}.sqlite")

        d = {}
        d["id"] = db_id
        d["question"] = question
        d["original_query"] = orig_query

        

        schema = get_schema(path)
        
        pred_query = generate_sql(schema, good_prompt, question, topk=topk)
        match =  re.search(r"SELECT[\s\S]*?;", pred_query, re.IGNORECASE)
        pred_query = match.group(0).strip() if match else None
        d["pred_query"] = pred_query

        pred_result, pred_time = execute_query(path, pred_query)
        orig_result, orig_time = execute_query(path, orig_query)


        if pred_time and orig_time and pred_time > 0:
            time_ratio = orig_time / pred_time
        else:
            time_ratio = 0

        
        d["pred_time"] = pred_time
        d["orig_time"] = orig_time
        d["time_ratio"] = time_ratio

        print(f"\n--- Processing Example {i+1}/{total_len} ---")
        print(f"Question: {question}")
        print(f"  - Generated SQL: {pred_query}")

        
        if pred_result is not None and pred_result == orig_result:
            correct += 1
            d["check"] = True
            print("  - Result: ✅ Correct (Execution Match)")
        else:
            d["check"] = False
            print("  - Result: ❌ Incorrect (Execution Mismatch or Error)")
        data.append(d)
        accuracy = (correct / (i + 1)) * 100 if total_len > 0 else 0
        print(f"Accuracy = {accuracy}")
        
        time.sleep(10)

    file_path_data=os.path.join("spider",f"results_{version_name}.json")
    with open(file_path_data,'w') as f:
        json.dump(data,f,indent=4)
         


    accuracy = (correct / (i + 1)) * 100 if total_len > 0 else 0
    ves = compute_ves(data)
    print("\n--- Evaluation Complete ---")
    print(f"Execution Accuracy on {i + 1} examples is: {accuracy:.2f}%")
    print(f"Valid Efficiency Score (VES): {ves:.2f}")

    summary_path = f"{version_name}.txt"
    with open(summary_path, "w") as f:
        f.write(f"Execution Accuracy: {accuracy:.2f}%\n")
        f.write(f"Valid Efficiency Score (VES): {ves:.2f}\n")

    print(f"Results saved as {summary_path}")
    return accuracy, ves