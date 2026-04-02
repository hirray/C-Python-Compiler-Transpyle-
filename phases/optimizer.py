def optimize_code(ir_code):
    optimized_code = []

    for line in ir_code:
        line = line.strip()

        # DO NOT remove { }
        if not line:
            optimized_code.append("")
            continue

        optimized_code.append(line)

    return optimized_code