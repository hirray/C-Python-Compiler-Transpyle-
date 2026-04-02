import re

def remove_comments(text):
    """
    Removes C-style comments from a source text string.
    Supports:
    - Multi-line /* ... */
    - Single-line // ...
    """
    
    # 1. Regex for multi-line comments: /* ... */
    # (flags=re.DOTALL ensures . matches newlines)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # 2. Regex for single-line comments: // ...
    # (only matches outside of string literals? No, for simple compiler, global is fine)
    # However, to be slightly safer, we regex for // that is NOT inside quotes.
    # For now, let's keep it simple as per project scope.
    text = re.sub(r'//.*', '', text)
    
    return text
