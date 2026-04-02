# ==============================
# C RETURN TYPES
# ==============================

C_RETURN_TYPES = {"int", "void", "char", "float", "double", "long", "short", "unsigned", "signed"}

# ==============================
# I/O FUNCTIONS
# ==============================

IO_MAP = {
    "printf": "print",
    "scanf":  "input",
    "puts":   "print",
}

# ==============================
# CONDITIONALS
# ==============================

CONDITIONAL_MAP = {
    "if":      "if",
    "else if": "elif",
    "else":    "else",
}

# ==============================
# OPERATORS
# ==============================

OPERATOR_MAP = {
    "&&": "and",
    "||": "or",
    # NOTE: '!' is deliberately NOT included here because simple string replace
    # would corrupt '!=' comparisons. It is handled in context by the parser.
}

# ==============================
# COMPARISON OPERATORS (kept as-is in Python)
# ==============================

COMPARISON_OPS = {"==", "!=", ">=", "<=", ">", "<"}

# ==============================
# INCREMENT / DECREMENT
# ==============================

INC_DEC_MAP = {
    "++": "+= 1",
    "--": "-= 1",
}

# ==============================
# DATA TYPES (Task-3 REMOVE)
# ==============================

DATA_TYPES = [
    "int",
    "float",
    "double",
    "char",
    "long",
    "short",
    "unsigned",
    "signed",
]

# ==============================
# SYMBOLS (REMOVE)
# ==============================

REMOVE_SYMBOLS = [";", "{", "}"]

# ==============================
# COMMENTS
# ==============================

COMMENT_MAP = {
    "//": "#",
    "/*": "'''",
    "*/": "'''",
}

# ==============================
# FORMAT SPECIFIERS -> Python types for scanf
# ==============================

SCANF_TYPE_MAP = {
    "%d": "int",
    "%f": "float",
    "%lf": "float",
    "%c": "str",
    "%s": "str",
    "%ld": "int",
    "%i": "int",
}

# ==============================
# FORMAT SPECIFIERS (for printf f-string conversion)
# ==============================

FORMAT_SPECIFIERS = ["%d", "%f", "%lf", "%c", "%s", "%ld", "%i"]

# ==============================
# REMOVE COMPLETELY
# ==============================

REMOVE_PATTERNS = [
    "#include<stdio.h>",
    "#include <stdio.h>",
    "main()",
]