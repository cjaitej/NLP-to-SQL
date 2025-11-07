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


    sub_path = (
    os.path.join("spider", "dev_subset.json")
    if data_set == "spider"
    else os.path.join("data", "bird", "dev_subset.json")
)
    with open(sub_path, "r") as f:
        dev_data = json.load(f)

    
    data_to_evaluate = dev_data 
    evaluate(data_to_evaluate, good_prompt, data_set, version_name)



if __name__ == "__main__":
    data_set = preprocessing()
    version_name = f"{data_set}_fewshot"
    main()
