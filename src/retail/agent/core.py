"""
Agent core - orchestrates the flow from question to answer.
"""

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from retail.config.settings import settings
from retail.ontology.query_builder.translator import NLToSQLTranslator
from retail.data.access.repository import SalesRepository, CustomerRepository, ProductRepository

class RetailAgent:
    """
    Retail AI Agent that answers customer questions by directly querying the data warehouse.
    
    Flow:
    1. Receive natural language question
    2. Translate to SQL using the ontology and LLM
    3. Execute SQL query against the data warehouse
    4. Format and return the answer
    """

    def __init__(self):
        self.translator = NLToSQLTranslator()
        self._engine = None
        self._Session = None

    def _get_session(self):
        """Get a database session."""
        if self._Session is None:
            self._engine = create_engine(f"duckdb:///{settings.DUCKDB_DATABASE_PATH}")
            self._Session = sessionmaker(bind=self._engine)
        return self._Session()

    def ask(self, question: str) -> str:
        """
        Ask a question to the retail AI agent.
        
        Args:
            question: Natural language question about the retail data
            
        Returns:
            Answer to the question
        """
        # Step 1: Translate the question to SQL
        sql = self.translator.translate(question)
        
        # Step 2: Execute the SQL query
        with self._get_session() as session:
            result = session.execute(sql)
            rows = result.fetchall()
            columns = result.keys()
        
        # Step 3: Format the answer
        return self._format_answer(question, sql, rows, columns)

    def _format_answer(self, question: str, sql: str, rows: list, columns: list) -> str:
        """
        Format the query result into a natural language answer.
        """
        if not rows:
            return f"I couldn't find any data matching your question: '{question}'"
        
        # Simple formatting for now
        if len(rows) == 1 and len(columns) == 1:
            # Single value result
            value = rows[0][0]
            if isinstance(value, float):
                value = f"${value:,.2f}"
            return f"The answer to '{question}' is: {value}"
        
        # Multiple values or multiple columns
        lines = [f"Results for: '{question}'"]
        lines.append("-" * 40)
        
        for row in rows:
            row_str = " | ".join(str(v) for v in row)
            lines.append(row_str)
        
        return "\n".join(lines)

    def execute_sql(self, sql: str) -> list:
        """
        Execute a raw SQL query and return the results.
        This is useful for debugging or advanced queries.
        """
        with self._get_session() as session:
            result = session.execute(sql)
            rows = result.fetchall()
            columns = result.keys()
        return rows, columns