# =========================================
# PHASE 4: INTERMEDIATE CODE GENERATION
# =========================================

import re
from utils.mappings import OPERATOR_MAP, INC_DEC_MAP, SCANF_TYPE_MAP, FORMAT_SPECIFIERS


# =========================================
# HELPER: Apply logical operator mappings
# Only applies outside of quoted strings
# =========================================
def apply_operator_mapping(line, addressed_vars=None):
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
                part = re.sub(r'\b(\d*\.\d+|\d+\.)[fF]\b', r'\1', part)
                result.append(part)
        return "".join(result)

    for op, py_op in OPERATOR_MAP.items():
        line = line.replace(op, py_op)
    line = re.sub(r'\b(\d*\.\d+|\d+\.)[fF]\b', r'\1', line)

    # Handle struct/pointer usages
    line = line.replace("->", ".")
    
    # Handle pointer indirection / dereference regex *var -> var[0]
    line = re.sub(r'(^|\W)\*([a-zA-Z_]\w*)', r'\1\2[0]', line)
    
    # Handle address-of &var -> _REF___ protector temporarily
    line = re.sub(r'(^|\W)&([a-zA-Z_]\w*)', r'\1\2_REF___', line)

    # Handle malloc usage inline
    if "malloc" in line:
        line = re.sub(r'malloc\s*\((.*)\)', lambda m: f"[0] * ({re.sub(r'sizeof\s*\([^)]+\)', '1', m.group(1))})", line)

    # Addressed Variables Reference Mapping -> replace primitive var usages with var[0]
    if addressed_vars:
        for var in addressed_vars:
            line = re.sub(r'\b' + var + r'\b(?!\s*\[)', f'{var}[0]', line)
            
        # Restore addressed var protectors into raw references
        for var in addressed_vars:
            line = line.replace(f'{var}_REF___', var)

    # Fallback to restore unknown references gracefully 
    line = re.sub(r'\b([a-zA-Z_]\w*)_REF___', r'\1', line)

    return line


# =========================================
# HELPER: Convert printf -> print
# Handles format specifiers -> f-strings
# e.g. printf("Val: %d\n", x)  ->  print(f"Val: {x}")
# e.g. printf("Hello\n")       ->  print("Hello")
# =========================================
def convert_printf(line, addressed_vars=None):
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

    # Check if there are format specifiers correctly formatted
    specifiers_found = re.findall(r'%[-+ #0]*\d*(?:\.\d+)?[dioufFeEgGxXcsSp]|%l[diouf]', inner)

    if not specifiers_found or not args:
        # No substitution needed
        inner_clean = inner.replace("\\", "")
        return f'print("{inner_clean}")'

    # Replace each specifier with {arg}
    result_inner = inner
    for arg in args:
        arg = apply_operator_mapping(arg, addressed_vars)
        # Match the FIRST remaining specifier tracking modifiers
        match = re.search(r'%([-+ #0]*\d*(?:\.\d+)?)([dioufFeEgGxXcsSp])|%l([diouf])', result_inner)
        if match:
            modifiers = match.group(1) or ""
            spec_type = match.group(2) or match.group(3)
            
            if spec_type == 's':
                # Convert list back to string if it was modified as a char array
                replacement = f"{{''.join({arg}) if isinstance({arg}, list) else {arg}}}"
            else:
                if modifiers:
                     replacement = f"{{{arg}:{modifiers}{spec_type}}}"
                else:
                     replacement = f"{{{arg}}}"
                     
            result_inner = result_inner[:match.start()] + replacement + result_inner[match.end():]

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


def convert_declaration(line, addressed_vars=None):
    if not addressed_vars: addressed_vars = set()
    line = line.strip().rstrip(";").strip()
    is_char = "char" in line.split()
    
    # Remove all C type keywords and modifiers from the beginning
    type_keywords = {"int", "float", "double", "char", "void", "long", "short", "unsigned", "signed", 
                     "const", "static", "volatile", "extern", "register", "struct", "union", "enum"}
    
    words = line.split()
    while words and words[0] in type_keywords:
        words.pop(0)
    
    if not words:
        return line

    rest = " ".join(words)
    # Split on top-level commas only
    segments = _split_top_level_commas(rest)

    results = []
    for seg in segments:
        seg = seg.strip()
        if "=" in seg:
            left, right = seg.split("=", 1)
            raw_left_name = left.replace("*", "").split("[")[0].split()[-1].strip()
            
            left_words = left.split()
            clean_left = [w for w in left_words if w not in type_keywords and w != "*"]
            left = " ".join(clean_left).replace("*", "")
            left = re.sub(r'\[.*?\]', '', left).strip()
            
            # Map the RHS normally
            right_val = apply_operator_mapping(right.strip(), addressed_vars)

            needs_boxing = (raw_left_name in addressed_vars) and ("[" not in seg.split("=")[0])

            if is_char and right_val.startswith('"') and right_val.endswith('"'):
                results.append(f"{left} = list({right_val})")
            elif needs_boxing:
                results.append(f"{left} = [{right_val}]")
            else:
                results.append(f"{left} = {right_val}")
        else:
            raw_left_name = seg.replace("*", "").split("[")[0].split()[-1].strip()
            seg_words = seg.split()
            clean_seg = [w for w in seg_words if w not in type_keywords and w != "*"]
            seg = " ".join(clean_seg).replace("*", "")
            seg = re.sub(r'\[.*?\]', '', seg).strip()
            if seg:
                needs_boxing = (raw_left_name in addressed_vars) and ("[" not in clean_seg) # originally not an array
                if needs_boxing:
                    results.append(f"{seg} = [None]")
                else:
                    results.append(f"{seg} = None")

    return "\n".join(results)


# =========================================
# MAIN INTERMEDIATE CODE GENERATOR
# =========================================

def generate_intermediate(parsed_data):
    ir_code = []
    nesting_depth = 0
    last_was_func_end = False  # track blank-line insertion between functions

    # Pre-scan identifying variables targeted by the 'address of' & operator
    addressed_vars = set()
    for stmt in parsed_data:
        matches = re.finditer(r'(^|\W)&([a-zA-Z_]\w*)', stmt["line"])
        for m in matches:
            addressed_vars.add(m.group(2))

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
            clean = line.replace(";", "").strip()
            if clean.startswith("free"):
                p_var = clean[clean.find("(")+1 : clean.rfind(")")].strip()
                ir_code.append(f"{p_var} = None")
            else:
                ir_code.append(clean)
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
            converted = convert_declaration(line, addressed_vars)
            ir_code.append(converted)
            continue

        # =========================================
        # ASSIGNMENT
        # =========================================
        if stmt_type == "assignment":
            if nesting_depth == 0: last_was_func_end = False
            clean = line.strip().rstrip(";")
            
            # Explicitly catch assignments to dereferenced pointers
            if clean.startswith("*"):
                left, right = clean.split("=", 1)
                left = left.strip()[1:] # strip *
                clean = f"{left}[0] = {right.strip()}"
                
            clean = apply_operator_mapping(clean, addressed_vars)
            ir_code.append(clean)
            continue

        # =========================================
        # OUTPUT (printf / puts)
        # =========================================
        if stmt_type == "output":
            ir_code.append(convert_printf(line, addressed_vars))
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
            condition = apply_operator_mapping(condition, addressed_vars)
            ir_code.append(f"if {condition}:")
            continue

        # =========================================
        # ELIF
        # =========================================
        if stmt_type == "elif":
            m = re.search(r'else\s+if\s*\((.+)\)', line)
            condition = m.group(1).strip() if m else ""
            condition = apply_operator_mapping(condition, addressed_vars)
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
            condition = apply_operator_mapping(condition, addressed_vars)
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
        clean = apply_operator_mapping(clean, addressed_vars)
        if clean:
            if nesting_depth == 0:
                last_was_func_end = False
            ir_code.append(clean)

    return ir_code