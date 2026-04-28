"""
Nexa Compiler - Parser
Team Member: Abhinav
"""

from lexer import (
    TOKEN_KEYWORD, TOKEN_NUMBER, TOKEN_IDENTIFIER,
    TOKEN_OPERATOR, TOKEN_ASSIGN,
    TOKEN_LBRACKET, TOKEN_RBRACKET,
    TOKEN_LPAREN, TOKEN_RPAREN,
    TOKEN_EOF
)

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

class AssignNode:
    def __init__(self, name, expression, line):
        self.name = name
        self.expression = expression
        self.line = line

class ShowNode:
    def __init__(self, expression, line):
        self.expression = expression
        self.line = line

class WhenNode:
    def __init__(self, condition, if_body, else_body, line):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
        self.line = line

class RepeatNode:
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body = body
        self.line = line

class BinOpNode:
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class ConditionNode:
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class NumberNode:
    def __init__(self, value, line):
        self.value = int(value)
        self.line = line

class IdentifierNode:
    def __init__(self, name, line):
        self.name = name
        self.line = line

class ParserError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def expect(self, token_type, value=None):
        if self.current.type != token_type:
            raise ParserError(f"Expected {token_type} but got {self.current.type}", self.current.line)
        if value is not None and self.current.value != value:
            raise ParserError(f"Expected '{value}' but got '{self.current.value}'", self.current.line)
        token = self.current
        self.advance()
        return token

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        self.expect(TOKEN_KEYWORD, "begin")
        statements = self.parse_statement_list()
        self.expect(TOKEN_KEYWORD, "end")
        return ProgramNode(statements)

    def parse_statement_list(self):
        statements = []
        while (self.current.type != TOKEN_KEYWORD or self.current.value not in ("end", "otherwise")) and \
              self.current.type != TOKEN_RBRACKET and \
              self.current.type != TOKEN_EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        if self.current.type == TOKEN_IDENTIFIER:
            return self.parse_assignment()
        if self.current.type == TOKEN_KEYWORD and self.current.value == "show":
            return self.parse_show()
        if self.current.type == TOKEN_KEYWORD and self.current.value == "when":
            return self.parse_when()
        if self.current.type == TOKEN_KEYWORD and self.current.value == "repeat":
            return self.parse_repeat()
        
        raise ParserError(f"Unexpected token '{self.current.value}'", self.current.line)

    def parse_assignment(self):
        line = self.current.line
        name_token = self.expect(TOKEN_IDENTIFIER)
        self.expect(TOKEN_ASSIGN)
        expr = self.parse_expression()
        return AssignNode(name_token.value, expr, line)

    def parse_show(self):
        line = self.current.line
        self.expect(TOKEN_KEYWORD, "show")
        expr = self.parse_expression()
        return ShowNode(expr, line)

    def parse_when(self):
        line = self.current.line
        self.expect(TOKEN_KEYWORD, "when")
        self.expect(TOKEN_LPAREN)
        condition = self.parse_condition()
        self.expect(TOKEN_RPAREN)
        self.expect(TOKEN_LBRACKET)
        if_body = self.parse_statement_list()
        self.expect(TOKEN_RBRACKET)

        else_body = []
        if self.current.type == TOKEN_KEYWORD and self.current.value == "otherwise":
            self.advance()
            self.expect(TOKEN_LBRACKET)
            else_body = self.parse_statement_list()
            self.expect(TOKEN_RBRACKET)

        return WhenNode(condition, if_body, else_body, line)

    def parse_repeat(self):
        line = self.current.line
        self.expect(TOKEN_KEYWORD, "repeat")
        self.expect(TOKEN_LPAREN)
        condition = self.parse_condition()
        self.expect(TOKEN_RPAREN)
        self.expect(TOKEN_LBRACKET)
        body = self.parse_statement_list()
        self.expect(TOKEN_RBRACKET)
        return RepeatNode(condition, body, line)

    def parse_expression(self):
        left = self.parse_term()
        while self.current.type == TOKEN_OPERATOR and self.current.value in ('+', '-'):
            op = self.current.value
            line = self.current.line
            self.advance()
            right = self.parse_term()
            left = BinOpNode(left, op, right, line)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current.type == TOKEN_OPERATOR and self.current.value in ('*', '/'):
            op = self.current.value
            line = self.current.line
            self.advance()
            right = self.parse_factor()
            left = BinOpNode(left, op, right, line)
        return left

    def parse_factor(self):
        if self.current.type == TOKEN_NUMBER:
            token = self.current
            self.advance()
            return NumberNode(token.value, token.line)
        if self.current.type == TOKEN_IDENTIFIER:
            token = self.current
            self.advance()
            return IdentifierNode(token.name if hasattr(token, 'name') else token.value, token.line)
        if self.current.type == TOKEN_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TOKEN_RPAREN)
            return expr
            
        raise ParserError(f"Unexpected token '{self.current.value}' in expression", self.current.line)

    def parse_condition(self):
        left = self.parse_expression()
        comp_ops = ('<', '>', '<=', '>=', '==', '!=')
        if self.current.type == TOKEN_OPERATOR and self.current.value in comp_ops:
            op = self.current.value
            line = self.current.line
            self.advance()
            right = self.parse_expression()
            return ConditionNode(left, op, right, line)
        raise ParserError(f"Expected a comparison operator", self.current.line)

def format_ast(node, prefix="", is_last=True):
    """Prints AST as a proper tree using branch characters."""
    lines = []

    if isinstance(node, ProgramNode):
        lines.append("Program")
        stmts = node.statements
        for i, stmt in enumerate(stmts):
            last = (i == len(stmts) - 1)
            conn = "└── " if last else "├── "
            ext  = "    " if last else "│   "
            lines.append(conn + _label(stmt))
            sub = _children_str(stmt, ext)
            if sub:
                lines.append(sub)
        return "\n".join(lines)

    return _label(node)


def _label(node):
    if isinstance(node, AssignNode):    return f"Assign: {node.name} <-"
    if isinstance(node, ShowNode):      return "Show"
    if isinstance(node, WhenNode):      return "When"
    if isinstance(node, RepeatNode):    return "Repeat"
    if isinstance(node, BinOpNode):     return f"BinOp [ {node.op} ]"
    if isinstance(node, ConditionNode): return f"Condition [ {node.op} ]"
    if isinstance(node, NumberNode):    return f"{node.value}"
    if isinstance(node, IdentifierNode):return f"{node.name}"
    return type(node).__name__


def _children_str(node, prefix):
    """Build the children lines for a given node."""
    pairs = _kids(node)
    if not pairs:
        return ""
    lines = []
    for i, (lbl, child) in enumerate(pairs):
        last = (i == len(pairs) - 1)
        conn = "└── " if last else "├── "
        ext  = "    " if last else "│   "

        if isinstance(child, list):
            lines.append(prefix + conn + lbl)
            for j, item in enumerate(child):
                l2 = (j == len(child) - 1)
                c2 = "└── " if l2 else "├── "
                e2 = "    " if l2 else "│   "
                lines.append(prefix + ext + c2 + _label(item))
                sub = _children_str(item, prefix + ext + e2)
                if sub:
                    lines.append(sub)
        else:
            lines.append(prefix + conn + _label(child))
            sub = _children_str(child, prefix + ext)
            if sub:
                lines.append(sub)
    return "\n".join(lines)


def _kids(node):
    """Return (label, child) pairs for each node type."""
    if isinstance(node, AssignNode):
        return [("value", node.expression)]
    if isinstance(node, ShowNode):
        return [("expr", node.expression)]
    if isinstance(node, WhenNode):
        result = [("condition", node.condition)]
        if node.if_body:  result.append(("if-body", node.if_body))
        if node.else_body: result.append(("otherwise", node.else_body))
        return result
    if isinstance(node, RepeatNode):
        return [("condition", node.condition), ("body", node.body)]
    if isinstance(node, BinOpNode):
        return [("left", node.left), ("right", node.right)]
    if isinstance(node, ConditionNode):
        return [("left", node.left), ("right", node.right)]
    return []
