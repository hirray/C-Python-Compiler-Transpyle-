# =========================================
# PHASE 2: SYNTAX ANALYSIS (PARSER)
# =========================================

import re

# C return types and modifiers - used to identify declarations and function DEFINITIONS
C_DECLARATION_KEYWORDS = {"int", "void", "char", "float", "double", "long", "short", "unsigned", "signed", "struct", "union", "enum", "const", "static", "volatile", "extern", "register"}

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
        cond = stripped[stripped.find("(")+1 : stripped.rfind(")")].strip()
        if not cond:
            return "error: Missing condition in if statement"
        return "if"

    # =========================================
    # For
    # =========================================
    if stripped.startswith("for") and "(" in stripped:
        cond = stripped[stripped.find("(")+1 : stripped.rfind(")")].strip()
        if not cond:
            return "error: Missing condition in for statement"
        return "for"

    # =========================================
    # While
    # =========================================
    if stripped.startswith("while") and "(" in stripped:
        cond = stripped[stripped.find("(")+1 : stripped.rfind(")")].strip()
        if not cond:
            return "error: Missing condition in while statement"
        return "while"

    # =========================================
    # Output (printf / puts)
    # =========================================
    if stripped.startswith("printf") or stripped.startswith("puts"):
        if not stripped.endswith(";"):
            return "error: Missing terminator (semicolon) in output statement"
        
        # Robust IO Argument Validation
        if stripped.startswith("printf"):
            m = re.match(r'printf\s*\(\s*(".*?")\s*((?:,\s*[^,\)]+)*)\s*\)\s*;', stripped)
            if not m:
                # Catch dangling commas: printf("...", );
                if re.search(r',\s*\)\s*;$', stripped):
                    return "error: Dangling comma or missing argument in printf"
                return "output" # Fallback if regex fails but basic syntax is ok

            fmt_string = m.group(1)[1:-1]
            args_raw = m.group(2).strip()
            
            # Count specifiers
            specifiers = re.findall(r'%[-+ #0]*\d*(?:\.\d+)?[dioufFeEgGxXcsSp]|%l[diouf]', fmt_string)
            # Count arguments (split by top-level commas)
            args = [a.strip() for a in args_raw.lstrip(",").split(",") if a.strip()]
            
            if len(specifiers) > len(args):
                return f"error: Missing argument for format specifier (expected {len(specifiers)}, got {len(args)})"
            elif len(specifiers) < len(args):
                return f"error: Too many arguments for format specifier (expected {len(specifiers)}, got {len(args)})"
        
        return "output"

    # =========================================
    # Input (scanf / gets)
    # =========================================
    if stripped.startswith("scanf") or stripped.startswith("gets"):
        if not stripped.endswith(";"):
            return "error: Missing terminator (semicolon) in input statement"
            
        if stripped.startswith("scanf"):
             # Simple validation for scanf
             if re.search(r',\s*\)\s*;$', stripped):
                return "error: Dangling comma or missing argument in scanf"
        return "input"

    # =========================================
    # Increment / Decrement  (standalone: i++; or ++i;)
    # =========================================
    if ("++") in stripped or ("--") in stripped:
        if stripped.endswith(";"):
            return "increment"
        else:
            return "error: Missing terminator (semicolon) in increment/decrement statement"

    # =========================================
    # Declaration
    # =========================================
    first_token = stripped.split()[0] if stripped.split() else ""
    if first_token in C_DECLARATION_KEYWORDS:
        # Could be a variable declaration OR a function definition.
        # Function definition: has '(' and ')' and does NOT end with ';'
        clean = stripped.rstrip("{").strip()  # handle: int foo() {
        if "(" in clean and ")" in clean and not clean.endswith(";"):
            return "function"
            
        # Standard Variable Declaration validations
        if not stripped.endswith(";"):
            return "error: Missing terminator (semicolon) in variable declaration"
            
        # Catch empty Right hand side assignments
        if "=" in stripped:
            right_side = stripped.split("=", 1)[1].strip()
            if right_side == ";" or right_side == "":
                return "error: Missing value evaluation on right hand side of declaration"
                
        # Otherwise it's a plain variable declaration
        return "declaration"

    # =========================================
    # Function call  (name(...); )
    # =========================================
    if "(" in stripped and ")" in stripped:
        if not stripped.endswith(";") and not stripped.endswith("{"):
            if stripped.startswith("if") or stripped.startswith("while") or stripped.startswith("for") or stripped.startswith("switch"):
                pass # loops can skip
            else:
                return "error: Missing terminator (semicolon) in function call"
                
        if stripped.endswith(";"):
            func_name = stripped.split("(")[0].strip()
            # Exclude known keywords and IO functions already handled above
            if func_name not in CONTROL_KEYWORDS and func_name not in IO_FUNCTIONS:
                if func_name.replace("_", "").isalnum():
                    return "call"

    # =========================================
    # Assignment / expression statement
    # =========================================
    if "=" in stripped:
        if not stripped.endswith(";"):
            return "error: Missing terminator (semicolon) in assignment statement"
            
        parts = stripped.split("=", 1)
        left_side = parts[0].strip()
        right_side = parts[1].strip()
        
        if right_side == ";" or not right_side.rstrip(";").strip():
            return "error: Missing evaluation on right hand side of assignment"
            
        if not left_side:
            return "error: Missing target variable in assignment"
            
        return "assignment"

    # =========================================
    # Block end with code on same line (e.g.  } else {)
    # =========================================
    if "}" in stripped:
        return "block_end"

    return "error: Unrecognized syntax or missing data type"


# =========================================
# MAIN PARSER FUNCTION
# =========================================

from utils.preprocessor import remove_comments

def syntax_analysis(lines):
    parsed_data = []
    syntax_errors = []
    in_main = False       # track when we are inside main()'s body
    main_depth = 0        # brace depth inside main

    # Join lines back into a single string to handle multi-line comments
    full_text = "\n".join(lines)
    
    # Strip ALL comments (// and /* */)
    clean_text = remove_comments(full_text)
    
    # Re-split into lines
    clean_lines = clean_text.split("\n")

    # [NEW] PHASE 2.1: Structural Integrity Verification (Braces/Parentheses)
    # =========================================
    brace_stack = []
    paren_stack = []
    
    char_text = "".join(clean_lines)
    for i, char in enumerate(char_text):
        if char == '{': brace_stack.append(i)
        elif char == '}':
            if not brace_stack:
                syntax_errors.append("Syntax Error (Mismatched '}' - closing brace without opening brace)")
                break
            brace_stack.pop()
        elif char == '(': paren_stack.append(i)
        elif char == ')':
            if not paren_stack:
                syntax_errors.append("Syntax Error (Mismatched ')' - closing parenthesis without opening parenthesis)")
                break
            paren_stack.pop()
            
    if brace_stack:
        syntax_errors.append("Syntax Error (Mismatched '{' - unclosed opening brace)")
    if paren_stack:
        syntax_errors.append("Syntax Error (Mismatched '(' - unclosed opening parenthesis)")

    if syntax_errors:
        return [], syntax_errors

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

            # Catch explicit syntax errors!
            if stmt_type.startswith("error: "):
                error_msg = stmt_type.split("error: ")[1]
                syntax_errors.append(f"Syntax Error ({error_msg}) on line: '{raw_original}'")
                continue
            elif stmt_type == "unknown":
                syntax_errors.append(f"Syntax Error (Unrecognized structures) on line: '{raw_original}'")
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

    return parsed_data, syntax_errors