from typing import List, Dict, Any
import tree_sitter
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
from app.code_analysis.parser.base import LanguageParser

class PythonParser(LanguageParser):
    def __init__(self):
        self.language = tree_sitter.Language(tspython.language(), "python")
        self.parser = tree_sitter.Parser()
        self.parser.set_language(self.language)

    def parse(self, source_code: str) -> tree_sitter.Tree:
        return self.parser.parse(bytes(source_code, "utf8"))

    def extract_symbols(self, tree: tree_sitter.Tree, source_code: str) -> List[Dict]:
        query = self.language.query("""
            (class_definition name: (identifier) @class.name)
            (function_definition name: (identifier) @function.name)
        """)
        captures = query.captures(tree.root_node)
        
        symbols = []
        for node, capture_name in captures:
            symbols.append({
                "type": capture_name,
                "name": node.text.decode("utf8"),
                "start_line": node.start_point[0],
                "end_line": node.end_point[0],
            })
        return symbols

    def extract_imports(self, tree: tree_sitter.Tree, source_code: str) -> List[str]:
        query = self.language.query("""
            (import_statement) @import
            (import_from_statement) @import_from
        """)
        captures = query.captures(tree.root_node)
        return [node.text.decode("utf8") for node, _ in captures]

    def extract_relationships(self, tree: tree_sitter.Tree, source_code: str) -> List[Dict]:
        # Implementation to find calls and inheritances
        return []

class JavaParser(LanguageParser):
    def __init__(self):
        self.language = tree_sitter.Language(tsjava.language(), "java")
        self.parser = tree_sitter.Parser()
        self.parser.set_language(self.language)

    def parse(self, source_code: str) -> tree_sitter.Tree:
        return self.parser.parse(bytes(source_code, "utf8"))

    def extract_symbols(self, tree: tree_sitter.Tree, source_code: str) -> List[Dict]:
        query = self.language.query("""
            (class_declaration name: (identifier) @class.name)
            (method_declaration name: (identifier) @method.name)
        """)
        captures = query.captures(tree.root_node)
        symbols = []
        for node, capture_name in captures:
            symbols.append({
                "type": capture_name,
                "name": node.text.decode("utf8"),
                "start_line": node.start_point[0],
                "end_line": node.end_point[0],
            })
        return symbols

    def extract_imports(self, tree: tree_sitter.Tree, source_code: str) -> List[str]:
        query = self.language.query("""
            (import_declaration) @import
        """)
        captures = query.captures(tree.root_node)
        return [node.text.decode("utf8") for node, _ in captures]

    def extract_relationships(self, tree: tree_sitter.Tree, source_code: str) -> List[Dict]:
        return []
