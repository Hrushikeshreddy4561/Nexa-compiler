"""
Nexa Mini Compiler
Team Members: Nikhil, Abhinav, Varshith, Hrushikesh, Rajesh
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lexer import tokenize, LexerError
from parser import Parser, ParserError, format_ast
from semantic import SemanticAnalyser, SemanticError
from codegen import TACGenerator, Optimizer, TargetCodeGenerator
from executor import Executor, RuntimeError

def print_section(title):
    print(f"\n--- {title} ---")

def print_tokens(tokens):
    print(f"  {'No.':<6}{'Type':<14}{'Value':<16}{'Line':<6}")
    print(f"  {'-'*5:<6}{'-'*13:<14}{'-'*15:<16}{'-'*5:<6}")
    for i, tok in enumerate(tokens, 1):
        print(f"  {i:<6}{tok.type:<14}{tok.value:<16}{tok.line:<6}")

def print_symbol_table(rows):
    print(f"  {'Variable':<12}{'Type':<12}{'Scope':<10}{'Defined at Line':<16}")
    print(f"  {'-'*11:<12}{'-'*11:<12}{'-'*9:<10}{'-'*15:<16}")
    for name, vtype, scope, line in rows:
        print(f"  {name:<12}{vtype:<12}{scope:<10}{line:<16}")

def print_code(code_list, line_numbers=True):
    for i, instr in enumerate(code_list, 1):
        if line_numbers:
            print(f"  {i:>3}  {instr}")
        else:
            print(f"  {instr}")

def run_file(filename):
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    print()
    print(f"--- NEXA MINI COMPILER : {filename} ---")

    print_section("STAGE 1: TOKENS")
    try:
        tokens = tokenize(source_code)
        print_tokens(tokens)
        print(f"\n  Total tokens: {len(tokens)}")
    except LexerError as e:
        print(f"\n  [LEXICAL ERROR] Line {e.line}: {e}")
        return

    print_section("STAGE 2: AST")
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print(format_ast(ast))
    except ParserError as e:
        print(f"\n  [SYNTAX ERROR] Line {e.line}: {e}")
        return

    print_section("STAGE 3: SYMBOL TABLE")
    try:
        analyser = SemanticAnalyser()
        analyser.analyse(ast)
        rows = analyser.get_symbol_table()
        if rows:
            print_symbol_table(rows)
        else:
            print("  (no variables declared)")
    except SemanticError as e:
        print(f"\n  [SEMANTIC ERROR] Line {e.line}: {e}")
        return

    print_section("STAGE 4: THREE-ADDRESS CODE")
    tac_gen = TACGenerator()
    tac = tac_gen.generate(ast)
    print_code(tac)

    print_section("STAGE 5: OPTIMIZED CODE")
    optimizer = Optimizer()
    optimized = optimizer.optimize(tac)
    print_code(optimized)

    print_section("STAGE 6: TARGET CODE")
    target_gen = TargetCodeGenerator()
    target = target_gen.generate(optimized)
    print_code(target, line_numbers=False)

    print_section("STAGE 7: PROGRAM OUTPUT")
    try:
        executor = Executor()
        executor.execute(ast)
    except RuntimeError as e:
        print(f"\n  [RUNTIME ERROR] Line {e.line}: {e}")
        return

    print("\n--- Compilation and Execution Successful! ---\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.nx>")
    else:
        run_file(sys.argv[1])
