"""
Ontology query builder module.
"""

from retail.ontology.query_builder.translator import NLToSQLTranslator, translate_nl_to_sql
from retail.ontology.query_builder.validator import validate_sql

__all__ = ["NLToSQLTranslator", "translate_nl_to_sql", "validate_sql"]