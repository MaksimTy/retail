"""
Natural Language to SQL translator using LLM and ontology.
"""

from typing import Optional
from retail.agent.llm.factory import create_llm_provider
from .prompts import get_prompt
from .validator import validate_sql

class NLToSQLTranslator:
    """Translates natural language questions to SQL queries using an LLM."""

    def __init__(self):
        self.llm_provider = create_llm_provider()

    def translate(self, question: str) -> str:
        """
        Translate a natural language question to a SQL query.
        Steps:
        1. Generate a prompt using the few-shot examples.
        2. Use the LLM to generate the SQL query.
        3. Validate the generated SQL query.
        4. Return the validated SQL query.
        """
        if not self.llm_provider.is_available():
            raise RuntimeError("LLM provider is not available. Please check the configuration.")

        # Step 1: Generate the prompt
        prompt = get_prompt(question)

        # Step 2: Generate SQL using the LLM
        sql_response = self.llm_provider.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.0,  # Use low temperature for deterministic output
        )

        # Step 3: Clean and validate the SQL
        sql = self._clean_sql(sql_response)
        if not validate_sql(sql):
            raise ValueError(f"Generated SQL failed validation: {sql}")

        return sql

    def _clean_sql(self, sql: str) -> str:
        """
        Clean the generated SQL string.
        Remove any markdown formatting, extra whitespace, etc.
        """
        # Remove markdown code blocks if present
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.endswith("```"):
            sql = sql[:-3]
        # Also handle cases with just ```
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        # Strip whitespace
        sql = sql.strip()

        # Ensure the SQL ends with a semicolon
        if not sql.endswith(";"):
            sql += ";"

        return sql

# Convenience function for direct use
def translate_nl_to_sql(question: str) -> str:
    translator = NLToSQLTranslator()
    return translator.translate(question)