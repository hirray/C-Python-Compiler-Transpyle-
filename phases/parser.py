# =========================================
# PHASE 2: SYNTAX ANALYSIS (PARSER)
# =========================================

# C return types - used to identify function DEFINITIONS
C_RETURN_TYPES = {"int", "void", "char", "float", "double", "long", "short", "unsigned", "signed"}

# Keywords that can appear before '(' but are NOT function names
CONTROL_KEYWORDS = {"if", "else", "for", "while", "switch", "return", "do"}

# Known IO functions - handled separately
IO_FUNCTIONS = {"printf", "scanf", "fprintf", "fscanf", "sprintf", "sscanf", "puts", "gets"}


def identify_statement(line):
    stripped = line.strip()

    # =========================================
    # Empty line
    # =========================================
    if not stripped:
        return "empty"

    # =========================================
    # Standalone block markers
    # =========================================
    if stripped == "{":
        return "block_start"

    if stripped == "}":
        return "block_end"

    # =========================================
    # Header
    # =========================================
    if stripped.startswith("#include") or stripped.startswith("#define"):
        return "header"

    # =========================================
    # Main function - skip entirely
    # =========================================
    if stripped.startswith("int main") or stripped.startswith("void main"):
        return "main"

    # =========================================
    # Comments
    # =========================================
    if stripped.startswith("//"):
        return "comment"

    # =========================================
    # Return
    # =========================================
    if stripped.startswith("return"):
        return "return"

    # =========================================
    # else if  (must be checked BEFORE else)
    # =========================================
    if "else if" in stripped or "else if" in stripped:
        return "elif"

    # =========================================
    # Else
    # =========================================
    if stripped.startswith("else"):
        return "else"

    # =========================================
    # If
    # =========================================
    if stripped.startswith("if") and "(" in stripped:
        return "if"

    # =========================================
    # For
    # =========================================
    if stripped.startswith("for") and "(" in stripped:
        return "for"

    # =========================================
    # While
    # =========================================
    if stripped.startswith("while") and "(" in stripped:
        return "while"

    # =========================================
    # Output (printf / puts)
    # =========================================
    if stripped.startswith("printf") or stripped.startswith("puts"):
        return "output"

    # =========================================
    # Input (scanf / gets)
    # =========================================
    if stripped.startswith("scanf") or stripped.startswith("gets"):
        return "input"

    # =========================================
    # Increment / Decrement  (standalone: i++; or ++i;)
    # =========================================
    if ("++") in stripped or ("--") in stripped:
        if stripped.endswith(";"):
            return "increment"

    # =========================================
    # Declaration
    # =========================================
    first_token = stripped.split()[0] if stripped.split() else ""
    if first_token in C_RETURN_TYPES:
        # Could be a variable declaration OR a function definition.
        # Function definition: has '(' and ')' and does NOT end with ';'
        clean = stripped.rstrip("{").strip()  # handle: int foo() {
        if "(" in clean and ")" in clean and not clean.endswith(";"):
            return "function"
        # Otherwise it's a plain variable declaration
        return "declaration"

    # =========================================
    # Function call  (name(...); )
    # =========================================
    if "(" in stripped and ")" in stripped and stripped.endswith(";"):
        func_name = stripped.split("(")[0].strip()
        # Exclude known keywords and IO functions already handled above
        if func_name not in CONTROL_KEYWORDS and func_name not in IO_FUNCTIONS:
            if func_name.replace("_", "").isalnum():
                return "call"

    # =========================================
    # Assignment / expression statement
    # =========================================
    if "=" in stripped and stripped.endswith(";"):
        return "assignment"

    # =========================================
    # Block end with code on same line (e.g.  } else {)
    # =========================================
    if "}" in stripped:
        return "block_end"

    return "unknown"


# =========================================
# MAIN PARSER FUNCTION
# =========================================

from utils.preprocessor import remove_comments

def syntax_analysis(lines):
    parsed_data = []
    in_main = False       # track when we are inside main()'s body
    main_depth = 0        # brace depth inside main

    # Join lines back into a single string to handle multi-line comments
    full_text = "\n".join(lines)
    
    # Strip ALL comments (// and /* */)
    clean_text = remove_comments(full_text)
    
    # Re-split into lines
    clean_lines = clean_text.split("\n")

    for line in clean_lines:
        raw_original = line.strip()
        if not raw_original:
            continue

        # Compound Line Splitting (e.g., "} else {")
        # If a line starts with '}' but has more content, split it.
        if raw_original.startswith("}") and len(raw_original) > 1:
            # Check if it's actually followed by a keyword like else
            rest = raw_original[1:].strip()
            if rest.startswith("else") or rest.startswith("for") or rest.startswith("while"):
                virtual_lines = ["}", rest]
            else:
                virtual_lines = [raw_original]
        else:
            virtual_lines = [raw_original]

        for raw in virtual_lines:
            # Strip inline comment for classification purposes only
            classify_line = raw
            if "//" in raw:
                # preserve the raw original, but classify without inline comment
                in_str = False
                for i, ch in enumerate(raw):
                    if ch == '"':
                        in_str = not in_str
                    if not in_str and raw[i:i + 2] == '//':
                        classify_line = raw[:i].strip()
                        break

            stmt_type = identify_statement(classify_line)

            # Skip completely empty classifications
            if stmt_type == "empty":
                continue

            # Track main() body - skip its block markers so they don't appear in IR
            if stmt_type == "main":
                in_main = True
                main_depth = 0
                # Don't emit the main statement itself
                continue

            if in_main:
                if stmt_type == "block_start":
                    main_depth += 1
                    if main_depth == 1:
                        continue  # skip the opening { of main
                if stmt_type == "block_end":
                    if main_depth == 1:
                        in_main = False
                        main_depth = 0
                        continue  # skip the closing } of main
                    main_depth -= 1

            parsed_data.append({
                "line": raw,
                "type": stmt_type,
                "in_main": in_main
            })

    return parsed_data