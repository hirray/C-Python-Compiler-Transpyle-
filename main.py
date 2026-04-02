# =========================================
# MAIN DRIVER FILE
# =========================================

from phases.lexer import lexical_analysis
from phases.parser import syntax_analysis
from phases.semantic import semantic_analysis
from phases.intermediate import generate_intermediate
from phases.optimizer import optimize_code
from phases.generator import generate_python_code

def main():
    # Read input file
    try:
        with open("test/input.c", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: input.c not found in /test folder")
        return

    # =========================================
    # PHASE 1: LEXICAL ANALYSIS
    # =========================================
    tokens, symbol_table = lexical_analysis(lines)

    print("\n===== TOKENS =====")
    for token in tokens:
        print(token)

    print("\n===== SYMBOL TABLE =====")
    for key, value in symbol_table.items():
        print(f"{key} : {value}")

    # =========================================
    # PHASE 2: SYNTAX ANALYSIS
    # =========================================
    parsed = syntax_analysis(lines)

    print("\n===== PARSED OUTPUT =====")
    for item in parsed:
        print(item)

    print("\nPhase 1 & Phase 2 Completed Successfully!")
    
    # =========================================
    # PHASE 3: SEMANTIC ANALYSIS
    # =========================================
    symbol_table, errors = semantic_analysis(parsed, symbol_table)

    print("\n===== UPDATED SYMBOL TABLE =====")
    for key, value in symbol_table.items():
        print(f"{key} : {value}")

    print("\n===== SEMANTIC ERRORS =====")
    if errors:
        for e in errors:
            print(e)
    else:
        print("No semantic errors")
    

    # =========================================
    # PHASE 4
    # =========================================
    ir_code = generate_intermediate(parsed)

    print("\n===== INTERMEDIATE CODE =====")
    for line in ir_code:
        print(line)
    
    # =========================================
    # PHASE 5
    # =========================================
    optimized_code = optimize_code(ir_code)

    print("\n===== OPTIMIZED CODE =====")
    for line in optimized_code:
        print(line)

    # =========================================
    # PHASE 6
    # =========================================
    final_code = generate_python_code(optimized_code)

    print("\n===== FINAL PYTHON CODE =====")
    for line in final_code:
        print(line)

    # Save output
    with open("test/output.py", "w") as f:
        f.write("\n".join(final_code))

# =========================================
# RUN PROGRAM
# =========================================
if __name__ == "__main__":
    main()