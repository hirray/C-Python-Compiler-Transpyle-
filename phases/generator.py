# =========================================
# PHASE 6: FINAL CODE GENERATION
# Converts { } markers into Python indentation
# =========================================

def generate_python_code(ir_code):
    final_code = []
    indent     = 0

    for line in ir_code:
        line = line.strip()

        if not line:
            final_code.append("")
            continue

        # -- closing brace -> reduce indent, don't emit anything
        if line == "}":
            if indent > 0:
                indent -= 1
            continue

        # -- opening brace -> the previous line ending with ':' already
        #    increased indent; just skip the brace marker itself
        if line == "{":
            continue

        # -- emit the line with current indent
        final_code.append("    " * indent + line)

        # -- if this line opens a block, increase indent for next line
        if line.endswith(":"):
            indent += 1

    return final_code