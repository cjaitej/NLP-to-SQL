import json
import os
from utils import *


def main():
    #need to change this. we are using wrong prompt.
    good_prompt="""
        Below is an instruction that describes a task, paired with an input that provides further context.
        Write a response that appropriately completes the request.

        ### db_info:\n{db_schema}\n\n### Input:\n{user_question}\n\n### Response:
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
    evaluate(data_to_evaluate, good_prompt, data_set, version_name, provider)


if __name__ == "__main__":
    provider, data_set = preprocessing()
    version_name = f"{provider}_{data_set}_simple"
    main()