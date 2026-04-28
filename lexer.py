"""
Nexa Compiler - Lexer
Team Member: Nikhil
"""

TOKEN_KEYWORD    = "KEYWORD"
TOKEN_NUMBER     = "NUMBER"
TOKEN_IDENTIFIER = "IDENTIFIER"
TOKEN_OPERATOR   = "OPERATOR"
TOKEN_ASSIGN     = "ASSIGN"
TOKEN_LBRACKET   = "LBRACKET"
TOKEN_RBRACKET   = "RBRACKET"
TOKEN_LPAREN     = "LPAREN"
TOKEN_RPAREN     = "RPAREN"
TOKEN_EOF        = "EOF"

KEYWORDS = {"begin", "end", "show", "when", "otherwise", "repeat"}

class Token:
    def __init__(self, token_type, value, line):
        self.type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line})"

class LexerError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

def tokenize(source_code):
    tokens = []
    pos = 0
    line = 1
    length = len(source_code)

    while pos < length:
        char = source_code[pos]

        if char == '\n':
            line += 1
            pos += 1
            continue
        if char in (' ', '\t', '\r'):
            pos += 1
            continue

        if char == '/' and pos + 1 < length and source_code[pos + 1] == '/':
            while pos < length and source_code[pos] != '\n':
                pos += 1
            continue

        if char == '<' and pos + 1 < length and source_code[pos + 1] == '-':
            tokens.append(Token(TOKEN_ASSIGN, "<-", line))
            pos += 2
            continue

        if char in ('<', '>', '=', '!') and pos + 1 < length and source_code[pos + 1] == '=':
            tokens.append(Token(TOKEN_OPERATOR, char + '=', line))
            pos += 2
            continue

        if char in ('+', '-', '*', '/', '<', '>'):
            tokens.append(Token(TOKEN_OPERATOR, char, line))
            pos += 1
            continue

        if char == '[':
            tokens.append(Token(TOKEN_LBRACKET, "[", line))
            pos += 1
            continue
        if char == ']':
            tokens.append(Token(TOKEN_RBRACKET, "]", line))
            pos += 1
            continue
        if char == '(':
            tokens.append(Token(TOKEN_LPAREN, "(", line))
            pos += 1
            continue
        if char == ')':
            tokens.append(Token(TOKEN_RPAREN, ")", line))
            pos += 1
            continue

        if char.isdigit():
            start = pos
            while pos < length and source_code[pos].isdigit():
                pos += 1
            tokens.append(Token(TOKEN_NUMBER, source_code[start:pos], line))
            continue

        if char.isalpha() or char == '_':
            start = pos
            while pos < length and (source_code[pos].isalnum() or source_code[pos] == '_'):
                pos += 1
            word = source_code[start:pos]
            if word in KEYWORDS:
                tokens.append(Token(TOKEN_KEYWORD, word, line))
            else:
                tokens.append(Token(TOKEN_IDENTIFIER, word, line))
            continue

        raise LexerError(f"Unexpected character '{char}'", line)

    tokens.append(Token(TOKEN_EOF, "EOF", line))
    return tokens
