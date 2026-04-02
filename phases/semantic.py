def semantic_analysis(parsed_data, symbol_table):
    errors = []

    for stmt in parsed_data:
        line = stmt["line"]
        stmt_type = stmt["type"]

        # =========================================
        # HANDLE DECLARATION
        # =========================================
        if stmt_type == "declaration":
            parts = line.replace(";", "").split()

            # Example: int a = 5
            if len(parts) >= 2:
                dtype = parts[0]
                var_name = parts[1]

                if "(" in var_name:
                    continue

                if var_name not in symbol_table:
                    symbol_table[var_name] = {
                        "type": None,
                        "value": None
                    }

                symbol_table[var_name]["type"] = dtype

                if "=" in parts:
                    symbol_table[var_name]["value"] = parts[-1]

        # =========================================
        # HANDLE FOR LOOP DECLARATION
        # =========================================
        elif stmt_type == "for":
            if "int" in line:
                inside = line[line.find("(")+1 : line.find(")")]
                first_part = inside.split(";")[0]  # int i = 0

                temp = first_part.strip().split()

                if len(temp) >= 2:
                    dtype = temp[0]

                    if len(temp) >= 4 and temp[2] == "=":
                        var_name = temp[1]
                        value = temp[3]
                    else:
                        var_name = temp[1]
                        value = None

                    symbol_table[var_name] = {
                        "type": dtype,
                        "value": value
                    }

        # =========================================
        # HANDLE INCREMENT / DECREMENT
        # =========================================
        elif stmt_type == "increment":
            line = line.replace(";", "").strip()

            if "++" in line:
                var_name = line.replace("++", "").strip()

                if var_name not in symbol_table:
                    errors.append(f"Semantic Error: '{var_name}' not declared")

            elif "--" in line:
                var_name = line.replace("--", "").strip()

                if var_name not in symbol_table:
                    errors.append(f"Semantic Error: '{var_name}' not declared")

        # =========================================
        # CHECK VARIABLE USAGE (FIXED)
        # =========================================
        elif stmt_type in ["if", "while"]:
            import re
            
            # Use regex to find all potential identifiers (words)
            # and check if they are followed by an opening parenthesis '('
            matches = re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', line)
            
            for m in matches:
                word = m.group(1)
                
                # Look at the text immediately following the word
                after_word = line[m.end():].lstrip()
                
                # 1. Skip function names (identifier followed by '(')
                if after_word.startswith('('):
                    continue
                
                # 2. Skip keywords
                if word in ["if", "while", "else", "return", "int", "float", "double", "char"]:
                    continue
                
                # 3. Skip numbers (regex \b ensures we are looking at whole words, 
                # and [a-zA-Z_] ensures it starts with a letter/underscore if not digit)
                if not word[0].isdigit():
                    if word not in symbol_table:
                        errors.append(f"Semantic Error: '{word}' not declared")

        # =========================================
        # IGNORE OUTPUT STRINGS (IMPORTANT FIX)
        # =========================================
        elif stmt_type == "output":
            # DO NOT check inside printf
            continue

    return symbol_table, errors