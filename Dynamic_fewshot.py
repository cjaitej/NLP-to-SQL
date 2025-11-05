import json
from dotenv import load_dotenv
import google.generativeai as genai
import os
from utils import *
import time


def main():

    good_prompt = """You are an expert data scientist and SQL engineer.
        You are given a database schema and a natural language question.
        Your task is to carefully analyze the schema, reason about table relationships,
        and generate a correct and efficient SQL query that fully answers the question.
        Also be careful to only output valid SQL, no English text.

        Database Engine:
        SQLite

        Few-shot examples:
        {top_k}

        Now do the same for:

        Database Schema:
        {db_schema}

        Question:
        {user_question}

        -- Reasoning
        (2–6 lines)

        -- SQL Query
        Write only the SQL query (starting with SELECT and ending with ;

        Return output in the required format and nothing else.
    """

    sub_path = (
        os.path.join("spider", "dev_spider_filtered.json")
        if data_set == "spider"
        else os.path.join("data", "bird", "dev_bird_filtered.json")
    )

    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    evaluate_dynamic_fewshot(dev_data, good_prompt, top_k, data_set, version_name)

if __name__ == "__main__":
    data_set = preprocessing()
    version_name = f"{data_set}_dynamic_fewshot"
    top_k = 5
    main()
