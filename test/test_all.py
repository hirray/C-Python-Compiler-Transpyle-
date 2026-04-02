import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

# Import compiler phases
from phases.lexer import lexical_analysis
from phases.parser import syntax_analysis
from phases.semantic import semantic_analysis
from phases.intermediate import generate_intermediate
from phases.optimizer import optimize_code
from phases.generator import generate_python_code

def run_comprehensive_test():
    print("=========================================")
    print("COMPILER ENGINE - FULL PIPELINE TEST")
    print("=========================================\n")
    
    # 1. Read the comprehensive C file
    try:
        with open("test/comprehensive_test.c", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: test/comprehensive_test.c not found")
        return

    print("TESTING: test/comprehensive_test.c")
    
    # 2. RUN FULL PIPELINE
    try:
        # Phase 1: Lexical
        tokens, symbol_table = lexical_analysis(lines)
        print("Phase 1: Lexical Analysis Complete")
        
        # Phase 2: Parser
        parsed = syntax_analysis(lines)
        print("Phase 2: Syntax Analysis (Parser) Complete")
        
        # Phase 3: Semantic
        symbol_table, errors = semantic_analysis(parsed, symbol_table)
        if errors:
            print("Phase 3: Semantic Analysis FAILED")
            for e in errors: print(e)
            return
        print("Phase 3: Semantic Analysis Clean")
        
        # Phase 4: Intermediate
        ir_code = generate_intermediate(parsed)
        print("Phase 4: Intermediate Code Generation Complete")
        
        # Phase 5: Optimizer
        optimized_code = optimize_code(ir_code)
        print("Phase 5: Code Optimization Complete")
        
        # Phase 6: Generator
        final_py = generate_python_code(optimized_code)
        print("Phase 6: Python Generation Complete\n")
        
        # 3. PRINT RESULTS
        print("===== TRANSLATED PYTHON CODE =====")
        print("\n".join(final_py))
        print("==================================\n")
        
        # Save output for review
        with open("test/comprehensive_test.py", "w") as f:
            f.write("\n".join(final_py))
        print("Result saved to: test/comprehensive_test.py")
        print("\nCOMPLETE TEST SUCCESSFUL!")
        
    except Exception as e:
        print(f"CRITICAL ERROR during pipeline execution: {str(e)}")

if __name__ == "__main__":
    run_comprehensive_test()
