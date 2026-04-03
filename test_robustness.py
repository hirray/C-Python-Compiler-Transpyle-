from phases.parser import syntax_analysis

test_cases = [
    # 1. Missing printf argument
    "printf(\"Hello %d\", );",
    # 2. Specifier mismatch
    "printf(\"Val: %d %f\", x);",
    # 3. Empty assignment
    "x = ;",
    # 4. Mismatched structural elements
    "int main() { printf(\"hi\"); ", # Missing closing brace
    "if (x == 5 { printf(\"hi\"); }" # Missing closing parenthesis
]

print("===== RUNNING ROBUSTNESS TESTS =====")
for i, case in enumerate(test_cases, 1):
    print(f"\nTest {i}: {case}")
    # For structural tests, we need to pass them as a list to syntax_analysis
    lines = [case] if i < 4 else [case, "}"] if i == 4 else [case]
    parsed, errors = syntax_analysis(lines)
    if errors:
        for e in errors:
            print(f"  [DETECTED] {e}")
    else:
        print("  [FAILED] No error detected")
