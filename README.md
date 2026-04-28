# Nexa Mini Compiler

This is a custom mini compiler built in Python for our college project. It compiles and executes a simple toy language called "Nexa". 

We built this entirely from scratch without using any compiler-generator tools like Lex or Yacc. The main goal was to understand how the different phases of a compiler work together. When you run a program, it prints out the intermediate results of every single stage so you can see exactly what's happening under the hood.

## Features

The compiler pipeline includes 7 stages:
1. **Lexical Analysis** (`lexer.py`): Breaks the source code down into tokens.
2. **Syntax Analysis** (`parser.py`): Parses the tokens and builds an Abstract Syntax Tree (AST) using a recursive descent parser.
3. **Semantic Analysis** (`semantic.py`): Checks for undefined variables and generates a Symbol Table.
4. **Intermediate Code** (`codegen.py`): Converts the AST into Three-Address Code (TAC).
5. **Optimization** (`codegen.py`): Performs basic constant folding and copy propagation to clean up the TAC.
6. **Target Code** (`codegen.py`): Translates the optimized code into a pseudo-assembly language (using virtual registers like `R0`, `R1`).
7. **Execution** (`executor.py`): An interpreter that runs the validated AST and prints the final output.

## Language Syntax

Nexa is a very basic language. It supports integer arithmetic, variables, basic conditionals, and loops.

```text
begin
    // This is a comment
    math <- 40
    science <- 45
    total <- math + science
    
    show total
    
    when (total >= 50) [
        show total
    ] otherwise [
        show 0
    ]
    
    count <- 3
    repeat (count > 0) [
        show count
        count <- count - 1
    ]
end
```

## Team Members

This project was built by a team of 5:
- **Nikhil** — Lexer (`lexer.py`)
- **Abhinav** — Parser (`parser.py`)
- **Varshith** — Semantic Analyzer (`semantic.py`)
- **Hrushikesh** — Executor (`executor.py`)
- **Rajesh** — Code Generator (`codegen.py`)

All of us collaborated on the main driver script (`main.py`) which ties everything together.

## How to Run

You just need Python 3 installed. No external dependencies are required.

1. Clone or download this folder.
2. Open your terminal and navigate to the project directory.
3. Run the compiler using `main.py` and pass the `.nx` file you want to run.

```bash
# Run a correct program
python main.py samples/correct.nx

# Test the syntax error handling
python main.py samples/syntax_error.nx

# Test the semantic error handling
python main.py samples/semantic_error.nx
```

If you write your own program, just save it as a `.nx` file and pass it to `main.py` the exact same way.
