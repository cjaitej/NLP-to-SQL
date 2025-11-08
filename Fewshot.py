import json
import os
from utils import *

def main():

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

Write only the SQL query (starting with SELECT and ending with ;

Return output in the required format and nothing else.
"""
#     good_prompt = """You are an expert data scientist and SQL engineer. You are given a database schema and a natural language question. Your task is to carefully analyze the schema, reason about table relationships, and generate a correct and efficient SQLite query that fully answers the question.

# Database Engine:
# SQLite

# Follow the reasoning and query structure as shown in the few-shot examples below.

# Example 1:
# -- Question
# Which active district has the highest average score in Reading?

# -- Reasoning
# We need the district name and the corresponding average reading score. Join the schools table with satscores using CDSCode, filter for active districts, sort by reading score in descending order, and return the top one.

# -- SQL Query
# SELECT T1.District
# FROM schools AS T1
# INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds
# WHERE T1.StatusType = 'Active'
# ORDER BY T2.AvgScrRead DESC
# LIMIT 1;

# Example 2:
# -- Question
# Find the full name of members whose t-shirt size is extra large.

# -- Reasoning
# We select first and last names of all members from the member table where the t-shirt size column matches 'X-Large'.

# -- SQL Query
# SELECT first_name, last_name
# FROM member
# WHERE t_shirt_size = 'X-Large';

# Example 3:
# -- Question
# Which country is the oldest driver from?

# -- Reasoning
# We look for the earliest date of birth (dob) in the drivers table and return the nationality corresponding to that record.

# -- SQL Query
# SELECT nationality
# FROM drivers
# WHERE dob IS NOT NULL
# ORDER BY dob ASC
# LIMIT 1;

# Example 4:
# -- Question
# Which districts have transactions greater than $10,000 in 1997?

# -- Reasoning
# We join account, district, and trans tables using their IDs, filter transactions from the year 1997, group by district, and return those having total transaction amounts greater than 10,000.

# -- SQL Query
# SELECT T1.district_id
# FROM account AS T1
# INNER JOIN district AS T2 ON T1.district_id = T2.district_id
# INNER JOIN trans AS T3 ON T1.account_id = T3.account_id
# WHERE STRFTIME('%Y', T3.date) = '1997'
# GROUP BY T1.district_id
# HAVING SUM(T3.amount) > 10000;

# Example 5:
# -- Question
# How many cards have infinite power?

# -- Reasoning
# We simply count all rows in the cards table where the power attribute equals '*', which represents infinity.

# -- SQL Query
# SELECT COUNT(*)
# FROM cards
# WHERE power = '*';

# Now, for the following schema and question, follow the same reasoning process and output format:

# Database Schema:
# {db_schema}

# Question:
# {user_question}

# -- Reasoning
# (Concise 2–6 line logical explanation describing how you derived the query)

# -- SQL Query

# Write only the SQL query (starting with SELECT and ending with ;

# Return output in the required format and nothing else.
# """


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
    version_name = f"{provider}_{data_set}_fewshot"
    main()