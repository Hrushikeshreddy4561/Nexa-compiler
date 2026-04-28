"""
Nexa Compiler - Semantic Analyzer
Team Member: Varshith
"""

from parser import (
    ProgramNode, AssignNode, ShowNode, WhenNode, RepeatNode,
    BinOpNode, ConditionNode, NumberNode, IdentifierNode
)

class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

class SemanticAnalyser:
    def __init__(self):
        self.defined_vars = set()
        self.symbol_table = {}

    def analyse(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.analyse(stmt)
        elif isinstance(node, AssignNode):
            self.analyse(node.expression)
            self.defined_vars.add(node.name)
            if node.name not in self.symbol_table:
                self.symbol_table[node.name] = {
                    "type": "INTEGER",
                    "line": node.line,
                    "scope": "global"
                }
        elif isinstance(node, ShowNode):
            self.analyse(node.expression)
        elif isinstance(node, WhenNode):
            self.analyse(node.condition)
            for s in node.if_body:
                self.analyse(s)
            for s in node.else_body:
                self.analyse(s)
        elif isinstance(node, RepeatNode):
            self.analyse(node.condition)
            for s in node.body:
                self.analyse(s)
        elif isinstance(node, BinOpNode):
            self.analyse(node.left)
            self.analyse(node.right)
        elif isinstance(node, ConditionNode):
            self.analyse(node.left)
            self.analyse(node.right)
        elif isinstance(node, NumberNode):
            pass
        elif isinstance(node, IdentifierNode):
            if node.name not in self.defined_vars:
                raise SemanticError(f"Undefined variable '{node.name}'", node.line)

    def get_symbol_table(self):
        rows = []
        for name, info in self.symbol_table.items():
            rows.append((name, info["type"], info["scope"], info["line"]))
        return rows
