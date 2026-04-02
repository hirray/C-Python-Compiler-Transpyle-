import re
from utils.mappings import DATA_TYPES

KEYWORDS = {
    "if", "else", "for", "while", "return",
    "printf", "scanf"
}

OPERATORS = {
    "+", "-", "*", "/", "=", "==", "!=", ">", "<", ">=", "<="
}

SYMBOLS = {
    "(", ")", "{", "}", ";", ","
}


def tokenize(line):
    # Handle strings properly
    tokens = re.findall(r'"[^"]*"|\w+|==|!=|>=|<=|[^\s\w]', line)
    return tokens


from utils.preprocessor import remove_comments

def lexical_analysis(lines):
    token_stream = []
    symbol_table = {}

    # Join lines back into a single string to handle multi-line comments
    full_text = "\n".join(lines)
    
    # Strip ALL comments (// and /* */)
    clean_text = remove_comments(full_text)
    
    # Re-split into lines
    clean_lines = clean_text.split("\n")

    for line in clean_lines:
        line = line.strip()
        if not line:
            continue

        # Skip header file completely
        if line.startswith("#include"):
            continue

        tokens = tokenize(line)

        for token in tokens:

            if token in KEYWORDS or token in DATA_TYPES:
                token_stream.append(("KEYWORD", token))

            elif token in OPERATORS:
                token_stream.append(("OPERATOR", token))

            elif token in SYMBOLS:
                token_stream.append(("SYMBOL", token))

            elif token.isdigit():
                token_stream.append(("CONSTANT", token))

            elif re.match(r'^".*"$', token):
                token_stream.append(("STRING", token))

            # Only valid identifiers
            elif re.match(r'^[a-zA-Z_]\w*$', token):
                token_stream.append(("IDENTIFIER", token))

                if token not in symbol_table:
                    symbol_table[token] = {
                        "type": None,
                        "value": None
                    }

            else:
                # ignore unwanted tokens like ., #, etc.
                continue

    return token_stream, symbol_table