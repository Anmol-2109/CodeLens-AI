from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LanguageParser(ABC):
    
    @abstractmethod
    def parse(self, source_code: str) -> Any:
        """Parses the source code into an AST."""
        pass

    @abstractmethod
    def extract_symbols(self, tree: Any, source_code: str) -> List[Dict]:
        """Extracts classes, methods, functions, etc."""
        pass

    @abstractmethod
    def extract_imports(self, tree: Any, source_code: str) -> List[str]:
        """Extracts imports and dependencies."""
        pass

    @abstractmethod
    def extract_relationships(self, tree: Any, source_code: str) -> List[Dict]:
        """Extracts structural relationships (e.g., class inherits from X)."""
        pass
