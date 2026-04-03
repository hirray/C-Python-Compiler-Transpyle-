from phases.parser import syntax_analysis

test_lines = [
    "int main() {",
    "    printf(\"Hello World\")",
    "    scanf(\"%d\", &n)",
    "    return 0;",
    "}"
]

parsed, errors = syntax_analysis(test_lines)

print("===== PARSED DATA =====")
for p in parsed:
    print(p)

print("\n===== SYNTAX ERRORS =====")
for e in errors:
    print(e)
