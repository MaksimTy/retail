"""
Concept registry for the ontology layer.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

class ConceptRegistry:
    """Registry for business concepts."""
    
    def __init__(self, definitions_path: Path):
        self.definitions_path = definitions_path
        self._concepts: Dict[str, Any] = {}
        self._load_definitions()
    
    def _load_definitions(self) -> None:
        """Load concept definitions from YAML file."""
        with open(self.definitions_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # The YAML structure is expected to be a list of concept definitions
        # or a dictionary with a 'concepts' key. We'll handle both.
        if isinstance(data, dict) and 'concepts' in data:
            concepts_list = data['concepts']
        elif isinstance(data, list):
            concepts_list = data
        else:
            # Assume the YAML is a mapping of concept name to definition
            concepts_list = [{'name': k, **v} for k, v in data.items()]
        
        for concept in concepts_list:
            name = concept.get('name')
            if name:
                self._concepts[name] = concept
    
    def get(self, name: str) -> dict | None:
        """Get a concept definition by name."""
        return self._concepts.get(name)
    
    def list_concepts(self) -> list[str]:
        """List all concept names."""
        return list(self._concepts.keys())
    
    def get_all(self) -> dict[str, dict]:
        """Get all concept definitions."""
        return self._concepts.copy()

# Default registry instance
concept_registry = ConceptRegistry(
    Path(__file__).parent.parent / "definitions.yaml"
)