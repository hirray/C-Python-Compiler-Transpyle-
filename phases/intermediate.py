# =========================================
# PHASE 4: INTERMEDIATE CODE GENERATION
# =========================================

import re
from utils.mappings import OPERATOR_MAP, INC_DEC_MAP, SCANF_TYPE_MAP, FORMAT_SPECIFIERS


# =========================================
# HELPER: Apply logical operator mappings
# Only applies outside of quoted strings
# =========================================
def apply_operator_mapping(line):
    # Do not touch string literals
    if '"' in line:
        # Only replace operators in the part OUTSIDE the string
        parts = re.split(r'(".*?")', line)
        result = []
        for part in parts:
            if part.startswith('"'):
                result.append(part)
            else:
                for op, py_op in OPERATOR_MAP.items():
                    part = part.replace(op, py_op)
                result.append(part)
        return "".join(result)

    for op, py_op in OPERATOR_MAP.items():
        line = line.replace(op, py_op)
    return line


# =========================================
# HELPER: Convert printf -> print
# Handles format specifiers -> f-strings
# e.g. printf("Val: %d\n", x)  ->  print(f"Val: {x}")
# e.g. printf("Hello\n")       ->  print("Hello")
# =========================================
def convert_printf(line):
    # Strip trailing ; and whitespace
    line = line.strip().rstrip(";").strip()

    # Match:  printf( "...", arg1, arg2, ... )
    # Also handle puts("...")
    m = re.match(r'(?:printf|puts)\s*\(\s*(".*?")\s*((?:,\s*[^,\)]+)*)\s*\)', line)
    if not m:
        # Fallback: simple replace
        line = line.replace("printf", "print").replace("puts", "print")
        return line

    fmt_string = m.group(1)            # e.g.  "Value: %d\n"
    args_raw   = m.group(2).strip()    # e.g.  ", x, y"

    # Parse arguments (strip leading comma)
    args = []
    if args_raw:
        args_raw = args_raw.lstrip(",").strip()
        args = [a.strip() for a in args_raw.split(",") if a.strip()]

    # Strip the outer quotes
    inner = fmt_string[1:-1]

    # Remove \n, \t (Python print adds newline automatically)
    inner = inner.replace("\\n", "").replace("\\t", "\t")

    # Check if there are format specifiers
    specifiers_found = re.findall(r'%[dioufFeEgGxXcsSp]|%l[diouf]', inner)

    if not specifiers_found or not args:
        # No substitution needed
        inner_clean = inner.replace("\\", "")
        return f'print("{inner_clean}")'

    # Replace each specifier with {arg}
    result_inner = inner
    for arg in args:
        # Replace the FIRST remaining specifier
        result_inner = re.sub(r'%[dioufFeEgGxXcsSp]|%l[diouf]', f'{{{arg}}}', result_inner, count=1)

    return f'print(f"{result_inner}")'


# =========================================
# HELPER: Convert scanf -> variable = type(input())
# e.g. scanf("%d", &n)  ->  n = int(input())
# e.g. scanf("%f", &x)  ->  x = float(input())
# =========================================
def convert_scanf(line):
    line = line.strip().rstrip(";").strip()

    m = re.match(r'scanf\s*\(\s*(".*?")\s*,\s*&(\w+)\s*\)', line)
    if not m:
        return "input()  # TODO: check variable"

    fmt_string = m.group(1)   # e.g. "%d"
    var_name   = m.group(2)   # e.g. "n"

    inner = fmt_string[1:-1].strip()  # e.g. %d

    py_type = SCANF_TYPE_MAP.get(inner, "int")

    if py_type == "str":
        return f'{var_name} = input()'
    else:
        return f'{var_name} = {py_type}(input())'


# =========================================
# HELPER: Convert for loop
# Handles: i < N, i <= N, i > N, i >= N
# Handles: i++ and i--
# =========================================
def convert_for_loop(line):
    # Extract inside parentheses
    m = re.search(r'for\s*\((.+)\)', line)
    if not m:
        return "for i in range(10):  # TODO: check loop"

    inside = m.group(1)
    parts  = inside.split(";")

    if len(parts) != 3:
        return f"for {inside}:  # TODO: check loop"

    init_part, cond_part, update_part = [p.strip() for p in parts]

    # Parse init:  int i = 0  OR  i = 0
    init_clean = re.sub(r'\b(?:int|float|double|char|long)\b', '', init_part).strip()
    # e.g.  i = 0
    init_var = init_clean.split("=")[0].strip()
    init_val = init_clean.split("=")[1].strip() if "=" in init_clean else "0"

    # Parse condition:  i < N  /  i <= N  /  i > N  /  i >= N
    cond_match = re.match(r'(\w+)\s*(<=|>=|<|>|!=|==)\s*(.+)', cond_part.strip())
    if not cond_match:
        return f"for {init_var} in range({init_val}, ?):  # TODO"

    loop_var = cond_match.group(1)
    op       = cond_match.group(2)
    bound    = cond_match.group(3).strip()

    # Parse update:  i++  /  i--  /  i += 2  /  i -= 1
    step = 1
    step_str = ""
    if "++" in update_part or "+= 1" in update_part:
        step = 1
    elif "--" in update_part or "-= 1" in update_part:
        step = -1
    else:
        step_m = re.search(r'[+\-]=\s*(\d+)', update_part)
        if step_m:
            val = int(step_m.group(1))
            step = val if "+" in update_part else -val

    # Build range()
    if op == "<":
        start, stop = init_val, bound
    elif op == "<=":
        start, stop = init_val, f"{bound} + 1"
    elif op == ">":
        start, stop, step = init_val, bound, -abs(step)
    elif op == ">=":
        start, stop, step = init_val, f"{bound} - 1", -abs(step)
    else:
        start, stop = init_val, bound

    if step == 1:
        if start == "0":
            return f"for {loop_var} in range({stop}):"
        else:
            return f"for {loop_var} in range({start}, {stop}):"
    else:
        return f"for {loop_var} in range({start}, {stop}, {step}):"


# =========================================
# HELPER: Convert declaration
# Handles:
#   int a = 5;             ->  a = 5
#   int a;                 ->  a = None
#   int a, b;              ->  a = None\nb = None
#   int sum = add(x, y);   ->  sum = add(x, y)   (NOT broken by commas inside ())
# =========================================
def _split_top_level_commas(s):
    """Split on commas that are NOT inside parentheses."""
    parts = []
    depth = 0
    current = []
    for ch in s:
        if ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return parts


def convert_declaration(line):
    line = line.strip().rstrip(";").strip()
    tokens = line.split(None, 1)   # split type from the rest

    if len(tokens) < 2:
        return line

    # Remove the type keyword (first token)
    rest = tokens[1]

    # Split on top-level commas only
    segments = _split_top_level_commas(rest)

    results = []
    for seg in segments:
        seg = seg.strip()
        if "=" in seg:
            results.append(seg)         # e.g.  a = 5  or  sum = add(x, y)
        else:
            results.append(f"{seg} = None")  # e.g.  a  ->  a = None

    return "\n".join(results)


# =========================================
# MAIN INTERMEDIATE CODE GENERATOR
# =========================================

def generate_intermediate(parsed_data):
    ir_code = []
    nesting_depth = 0
    last_was_func_end = False  # track blank-line insertion between functions

    for stmt in parsed_data:
        line     = stmt["line"]
        stmt_type = stmt["type"]

        # =========================================
        # SKIP (headers and main definition)
        # =========================================
        if stmt_type in ("header", "main"):
            continue

        # =========================================
        # COMMENTS
        # =========================================
        if stmt_type == "comment" or line.strip().startswith("//"):
            converted = line.strip()
            # Inline comment on its own line
            if converted.startswith("//"):
                converted = "# " + converted[2:].strip()
            ir_code.append(converted)
            continue

        # Inline comment on a code line
        if "//" in line:
            code_part, comment_part = line.split("//", 1)
            line = code_part.strip() + "  # " + comment_part.strip()

        # =========================================
        # BLOCK MARKERS
        # =========================================
        if stmt_type == "block_start":
            nesting_depth += 1
            ir_code.append("{")
            continue

        if stmt_type == "block_end":
            nesting_depth -= 1
            ir_code.append("}")
            if nesting_depth == 0:
                last_was_func_end = True
            continue

        # =========================================
        # FUNCTION DEFINITION
        # =========================================
        if stmt_type == "function":
            # Insert blank line before function if something was already there
            if ir_code and not last_was_func_end:
                 # maybe add blank line anyway if it's a top-level function?
                 # let's stick to the flag for now
                 pass

            if last_was_func_end:
                ir_code.append("")
            
            last_was_func_end = False

            # Strip trailing { from same-line  e.g. void foo() {
            clean = line.rstrip("{").strip()

            name_part = clean.split("(")[0].strip()
            params_raw = clean[clean.find("(")+1 : clean.rfind(")")]

            # Remove return type
            name_tokens = name_part.split()
            func_name = name_tokens[-1]   # last token is always the name

            # Clean parameters: strip type keywords
            param_list = []
            if params_raw.strip() and params_raw.strip() not in ("void", ""):
                for p in params_raw.split(","):
                    p = p.strip()
                    p_tokens = p.split()
                    if p_tokens:
                        param_list.append(p_tokens[-1])  # keep only the name

            params_clean = ", ".join(param_list)
            ir_code.append(f"def {func_name}({params_clean}):")
            continue

        # =========================================
        # FUNCTION CALL
        # =========================================
        if stmt_type == "call":
            if nesting_depth == 0: last_was_func_end = False
            ir_code.append(line.replace(";", "").strip())
            continue

        # =========================================
        # RETURN
        # =========================================
        if stmt_type == "return":
            if nesting_depth == 0: last_was_func_end = False
            clean = line.replace(";", "").strip()
            # Skip  return 0;  inside main (where it's redundant at top-level)
            if clean == "return 0" and stmt.get("in_main", False):
                continue
            ir_code.append(clean)
            continue

        # =========================================
        # DECLARATION
        # =========================================
        if stmt_type == "declaration":
            if nesting_depth == 0: last_was_func_end = False
            converted = convert_declaration(line)
            ir_code.append(converted)
            continue

        # =========================================
        # ASSIGNMENT
        # =========================================
        if stmt_type == "assignment":
            if nesting_depth == 0: last_was_func_end = False
            clean = line.strip().rstrip(";")
            clean = apply_operator_mapping(clean)
            ir_code.append(clean)
            continue

        # =========================================
        # OUTPUT (printf / puts)
        # =========================================
        if stmt_type == "output":
            ir_code.append(convert_printf(line))
            continue

        # =========================================
        # INPUT (scanf / gets)
        # =========================================
        if stmt_type == "input":
            ir_code.append(convert_scanf(line))
            continue

        # =========================================
        # IF
        # =========================================
        if stmt_type == "if":
            condition = line[line.find("(")+1 : line.rfind(")")].strip()
            condition = apply_operator_mapping(condition)
            ir_code.append(f"if {condition}:")
            continue

        # =========================================
        # ELIF
        # =========================================
        if stmt_type == "elif":
            m = re.search(r'else\s+if\s*\((.+)\)', line)
            condition = m.group(1).strip() if m else ""
            condition = apply_operator_mapping(condition)
            ir_code.append(f"elif {condition}:")
            continue

        # =========================================
        # ELSE
        # =========================================
        if stmt_type == "else":
            ir_code.append("else:")
            continue

        # =========================================
        # FOR
        # =========================================
        if stmt_type == "for":
            ir_code.append(convert_for_loop(line))
            continue

        # =========================================
        # WHILE
        # =========================================
        if stmt_type == "while":
            condition = line[line.find("(")+1 : line.rfind(")")].strip()
            condition = apply_operator_mapping(condition)
            ir_code.append(f"while {condition}:")
            continue

        # =========================================
        # INCREMENT / DECREMENT
        # =========================================
        if stmt_type == "increment":
            clean = line.replace(";", "").strip()
            for c_op, py_op in INC_DEC_MAP.items():
                if c_op in clean:
                    var = clean.replace(c_op, "").strip()
                    clean = f"{var} {py_op}"
                    break
            ir_code.append(clean)
            continue

        # =========================================
        # UNKNOWN - pass through cleaned
        # =========================================
        clean = line.strip().rstrip(";")
        clean = apply_operator_mapping(clean)
        if clean:
            if nesting_depth == 0:
                last_was_func_end = False
            ir_code.append(clean)

    return ir_code