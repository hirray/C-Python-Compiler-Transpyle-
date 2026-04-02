# C to Python Compiler

A modular compiler engine that translates C source code into PEP 8-compliant Python code. Designed with a clean 6-phase pipeline, this project serves as both a practical utility and an academic reference for compiler design.

---

## Key Features

*   **Full 6-Phase Pipeline**: Lexical Analysis, Syntax Analysis (Parser), Semantic Analysis, Intermediate Representation (IR), Code Optimization, and Final Generation.
*   **Logical Mapping**: Converts C-style blocks and loops (for, while, if-else) into precise Python indentation.
*   **Function Intelligence**: Supports function definitions and complex calls, including calls inside conditional statements.
*   **Robust Pre-Processing**: Handles both single-line (//) and multi-line (/* ... */) C comments without breaking logic.
*   **Detailed UI**: A side-by-side Streamlit dashboard for real-time translation and intermediate phase inspection.

---

## Installation and Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/c-to-python-compiler.git
    cd c-to-python-compiler
    ```

2.  **Install Dependencies**:
    The project requires Streamlit and Pandas for the web interface.
    ```bash
    pip install streamlit pandas
    ```

---

## How to Run

### 1. Web Interface (Recommended)
Launch the interactive dashboard to see the side-by-side translation and explore intermediate compiler phases.
```bash
streamlit run ui/app.py
```

### 2. Terminal Mode (CLI)
Run the compiler from your terminal to process the default input.c file.
```bash
python main.py
```

### 3. Comprehensive Test Suite
Execute the full battery of tests to verify the entire pipeline.
```bash
python test/test_all.py
```

---

## Project Structure

*   **phases/**: Logic for all 6 compiler phases.
*   **ui/**: Streamlit dashboard implementation.
*   **utils/**: Operator mappings, data types, and the comment pre-processor.
*   **test/**: C source files for testing and validation.

---

## Example Translation

**Input (C):**
```c
int num = 5;
if (num > 0) {
    printf("Positive Number");
}
```

**Output (Python):**
```python
num = 5
if num > 0:
    print("Positive Number")
```



