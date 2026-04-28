"""
Nexa Compiler - Executor
Team Member: Hrushikesh
"""

from parser import (
    ProgramNode, AssignNode, ShowNode, WhenNode, RepeatNode,
    BinOpNode, ConditionNode, NumberNode, IdentifierNode
)

class RuntimeError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

class Executor:
    def __init__(self):
        self.variables = {}
        self.output = []

    def execute(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.execute(stmt)
        elif isinstance(node, AssignNode):
            value = self.evaluate(node.expression)
            self.variables[node.name] = value
        elif isinstance(node, ShowNode):
            value = self.evaluate(node.expression)
            print(value)
            self.output.append(str(value))
        elif isinstance(node, WhenNode):
            if self.evaluate_condition(node.condition):
                for s in node.if_body:
                    self.execute(s)
            else:
                for s in node.else_body:
                    self.execute(s)
        elif isinstance(node, RepeatNode):
            limit = 10000
            count = 0
            while self.evaluate_condition(node.condition):
                for s in node.body:
                    self.execute(s)
                count += 1
                if count >= limit:
                    raise RuntimeError("Possible infinite loop detected", node.line)

    def evaluate(self, node):
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, IdentifierNode):
            return self.variables[node.name]
        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '+': return left + right
            elif node.op == '-': return left - right
            elif node.op == '*': return left * right
            elif node.op == '/':
                if right == 0:
                    raise RuntimeError("Division by zero", node.line)
                return left // right
                
    def evaluate_condition(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        if node.op == '<': return left < right
        elif node.op == '>': return left > right
        elif node.op == '<=': return left <= right
        elif node.op == '>=': return left >= right
        elif node.op == '==': return left == right
        elif node.op == '!=': return left != right
