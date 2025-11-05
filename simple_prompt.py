import json
import os
from utils import *


def main():
    #need to change this. we are using wrong prompt.
    good_prompt="""You are an expert in converting English questions to SQL queries!
        Database Engine:
        SQLite

        Database Schema:
        {db_schema}

        Question:
        {user_question}

        -- SQL Query:
        Write only the SQL query (starting with SELECT and ending with ;

        Return output in the required format and nothing else.
        """


    sub_path = (
    os.path.join("spider", "dev_subset.json")
    if data_set == "spider"
    else os.path.join("data", "bird", "dev_subset.json")
    )
    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    # CORRECTED: Loop and total length must match
    data_to_evaluate = dev_data # Let's test on 5 examples
    evaluate(data_to_evaluate, good_prompt, data_set, version_name)

if __name__ == "__main__":
    data_set = preprocessing()
    version_name = f"{data_set}_structured"
    main()