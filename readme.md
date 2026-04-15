# CalcScript

CalcScript is a minimalist, **math-first programming language** built with a custom compiler pipeline featuring a deterministic Lexer, Recursive-Descent Parser, and a Tree-Walking Evaluator. The project includes a modern, browser-based IDE powered by Vue 3 and a Flask-based execution API.

## 🚀 Features

* **Custom Compiler Pipeline**: Implements a full Lexer → Parser → Evaluator flow.
* **Variable Management**: Supports variable initialization with `let` and subsequent re-assignment.
* **Math-First Logic**: Strict adherence to mathematical order of operations (precedence) for addition, subtraction, multiplication, and division.
* **Modern Web IDE**: A dark-mode, minimalist frontend with real-time output, syntax highlighting via custom styles, and keyboard shortcuts.
* **Error Handling**: Provides descriptive runtime and syntax errors, including protection against division by zero and accessing undefined variables.

## 🛠️ Tech Stack

* **Backend**: Python, Flask (API), Flask-CORS.
* **Frontend**: Vue 3 (Composition API), Tailwind CSS.
* **Core Logic**: Pure Python implementation of lexing and parsing algorithms.

## 📋 Language Syntax

CalcScript supports basic arithmetic, variables, and comments:

```calcscript
# This is a comment
let x = 10 + 5       # Initialization
let y = x * 2        # Use of variables
print y              # Output: 30

y = y + 1            # Re-assignment
print y              # Output: 31

print (10 + 2) / 3   # Parentheses support
```

## 📂 Project Structure

* `/backend`
    * `app.py`: Flask server and API endpoints.
    * `lexer.py`: Tokenizes raw source code into meaningful units.
    * `parser.py`: Converts tokens into an Abstract Syntax Tree (AST).
    * `evaluator.py`: Walks the AST to execute the logic.
* `/frontend`
    * `index.html`: Single-page IDE with Vue 3 integration.

## 🚦 Getting Started

### 1. Start the Backend
Navigate to the backend directory and run the Flask server:
```bash
cd backend
python app.py
```
The API will be available at `http://localhost:5000`.

### 2. Launch the Frontend
Simply open `frontend/index.html` in any modern web browser. 

### 3. Execute Code
* Type your code in the editor.
* Press **▶ Run Code** or use `Ctrl + Enter` to execute.

## 🏗️ Compiler Architecture

1.  **Lexer**: Scans the source for numbers, identifiers, and operators. It promotes identifiers like `let` and `print` to reserved keywords.
2.  **Parser**: Uses a recursive-descent approach to enforce precedence (e.g., multiplication before addition) and builds the AST.
3.  **Evaluator**: Dispatches "visitor" methods to process each node in the AST, maintaining a local `symbol_table` for variable state.