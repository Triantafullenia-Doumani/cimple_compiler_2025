# Cimple Compiler

This project is an educational compiler for a simple programming language called **Cimple**. The compiler is implemented in **Python** and developed using **Visual Studio 2022**. It performs several phases of compilation:

- **Lexical Analysis:** Tokenizes the source code.
- **Syntax Analysis:** Uses a recursive descent parser to generate intermediate code (quads) and build a symbol table.
- **Intermediate Code Generation:** Produces quads representing program operations.
- **Assembly Code Generation:** Translates the quads into MIPS-like assembly using symbol table info.

---

## Features

- **Comprehensive Analysis**  
  Performs lexical analysis, syntax analysis, intermediate code generation, and assembly code generation.

- **Symbol Table Management**  
  Builds a dynamic symbol table during parsing for variables, parameters, and temporaries.

- **Intermediate Code**  
  Generates intermediate code (quads) saved in the `int/` directory.

- **Assembly Code**  
  Produces MIPS-like assembly code stored in the `asm/` directory.

- **Unit Testing**  
  Includes unit tests using Python's `unittest` module.

---

## How It Works

1. **Lexical Analysis**  
   Converts the source file into tokens (identifiers, numbers, keywords, etc).

2. **Syntax Analysis**  
   Parses tokens based on Cimple grammar to build quads and maintain the symbol table.

3. **Intermediate Code Generation**  
   Produces `.int` files representing assignments, expressions, and function calls.

4. **Assembly Code Generation**  
   Translates `.int` files into `.asm` MIPS-like code using memory offset data.

---

## How to Run

### Requirements

- Python 3.x  
- Visual Studio 2022 (for development)

### Running the Compiler

The main file is `cimple_compiler_2025.py`. It now accepts a source file as a command-line argument.

```bash
python3 cimple_compiler_2025.py example.ci
```

This will:
- Perform lexical and syntax analysis
- Generate `.int` code in the `int/` folder
- Generate `.asm` code in the `asm/` folder
- Print the symbol table and quads to the console

### Running the Tests

```bash
python3 -m unittest discover
```

This command will auto-discover and run all unit tests.

---

## Project Structure

- `cimple_compiler_2025.py` — Main compiler file.
- `tests/ci/` — Sample input files (`fibonacci.ci`, `factorial.ci`, etc).
- `int/` — Output directory for intermediate code.
- `asm/` — Output directory for assembly code.
- `test_cimple_compiler_2025.py` — Unit tests for validation.

---



