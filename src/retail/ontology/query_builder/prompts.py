"""
Few-shot prompts for natural language to SQL translation.
"""

# Define the schema for the LLM
SCHEMA = """
Tables:
1. dim_customer
   - customer_key (INTEGER, PRIMARY KEY)
   - customer_id (VARCHAR)
   - country (VARCHAR)

2. dim_product
   - product_key (INTEGER, PRIMARY KEY)
   - stock_code (VARCHAR)
   - description (VARCHAR)
   - unit_price (DOUBLE)

3. fact_sales
   - sale_key (INTEGER, PRIMARY KEY)
   - customer_key (INTEGER, FOREIGN KEY REFERENCES dim_customer(customer_key))
   - product_key (INTEGER, FOREIGN KEY REFERENCES dim_product(product_key))
   - invoice_no (VARCHAR)
   - invoice_date (TIMESTAMP)
   - quantity (INTEGER)
   - unit_price (DOUBLE)
   - line_total (DOUBLE)
"""

# Few-shot examples for SQL generation
EXAMPLES = [
    {
        "question": "What is the total revenue?",
        "sql": "SELECT SUM(line_total) AS total_revenue FROM fact_sales;"
    },
    {
        "question": "How many orders are there?",
        "sql": "SELECT COUNT(DISTINCT invoice_no) AS order_count FROM fact_sales;"
    },
    {
        "question": "What is the total revenue by country?",
        "sql": "SELECT c.country, SUM(f.line_total) AS total_revenue "
                 "FROM fact_sales f "
                 "JOIN dim_customer c ON f.customer_key = c.customer_key "
                 "GROUP BY c.country;"
    },
    {
        "question": "List the top 5 products by revenue.",
        "sql": "SELECT p.stock_code, p.description, SUM(f.line_total) AS total_revenue "
                 "FROM fact_sales f "
                 "JOIN dim_product p ON f.product_key = p.product_key "
                 "GROUP BY p.stock_code, p.description "
                 "ORDER BY total_revenue DESC "
                 "LIMIT 5;"
    },
    {
        "question": "How many customers are there in each country?",
        "sql": "SELECT country, COUNT(*) AS customer_count "
                 "FROM dim_customer "
                 "GROUP BY country;"
    }
]

def get_prompt(question: str) -> str:
    """
    Generate a prompt for the LLM to translate natural language to SQL.
    """
    prompt = f"""You are an expert in translating natural language questions into SQL queries.
Given the following database schema:

{SCHEMA}

And the following examples of natural language questions and their corresponding SQL queries:

"""
    for example in EXAMPLES:
        prompt += f"Question: {example['question']}\nSQL: {example['sql']}\n\n"

    prompt += f"""Now, translate the following natural language question into a SQL query.
Only output the SQL query, nothing else.

Question: {question}
SQL:"""
    return prompt