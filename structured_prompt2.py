import json
import os
from utils import *


def main():
    good_prompt="""You are an expert data scientist and SQL engineer.
      You are given a database schema and a natural language question.
        Your task is to carefully analyze the schema, reason about table relationships,
          and generate a correct and efficient SQLite query that fully answers the question.

        Database Engine:
        SQLite


        Now, for the following schema and question, follow the same reasoning process and output format:

        Database Schema:
        {db_schema}

        Question:
        {user_question}

        -- Reasoning
        (Concise 2–6 line logical explanation describing how you derived the query)

        -- SQL Query
        Write only the SQL query (starting with SELECT and ending with ;

        Return output in the required format and nothing else.
        """


    sub_path = os.path.join("spider", "dev_subset.json") if data_set=="spider" else os.path.join("data","bird","dev_subset.json")

    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    data_to_evaluate = dev_data # Let's test on 5 examples
    evaluate(data_to_evaluate, good_prompt, data_set, version_name, provider)



if __name__ == "__main__":
    provider, data_set = preprocessing()
    version_name = f"{provider}_{data_set}_structured"
    main()