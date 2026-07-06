"""
SQL validator for the ontology layer.
"""

import re

def validate_sql(sql: str) -> bool:
    """
    Validate the SQL query.
    This is a simple validation for demonstration purposes.
    In a production environment, you would use a proper SQL parser.
    """
    if not sql or not sql.strip():
        return False
    
    # Convert to uppercase for easier checking
    sql_upper = sql.strip().upper()
    
    # Check that the query starts with SELECT (we only allow SELECT for now)
    if not sql_upper.startswith("SELECT"):
        return False
    
    # Check for potentially dangerous operations (optional, for safety)
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "EXEC", "TRUNCATE"]
    for keyword in forbidden_keywords:
        if keyword in sql_upper:
            return False
    
    # Check for balanced parentheses (simple check)
    if sql.count('(') != sql.count(')'):
        return False
    
    # Check for basic SQL injection patterns (very basic)
    # In reality, use parameterized queries or a proper ORM/query builder.
    # We are just doing a simple check for demonstration.
    if ";" in sql and not sql.strip().endswith(";"):
        # Allow only one statement and it must end with a semicolon
        return False
    
    return True

if __name__ == "__main__":
    # Test the validator
    test_queries = [
        "SELECT SUM(line_total) AS total_revenue FROM fact_sales;",
        "SELECT * FROM fact_sales;",
        "INSERT INTO fact_sales VALUES (1, 1, 1, 'INV001', '2023-01-01', 1, 10.0, 10.0);",
        "SELECT * FROM fact_sales WHERE 1=1; DROP TABLE fact_sales;",
    ]
    for query in test_queries:
        print(f"Query: {query}")
        print(f"Valid: {validate_sql(query)}")
        print()