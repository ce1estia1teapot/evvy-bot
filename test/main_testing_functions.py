

def addition(a : int = None, b : int = None) -> int | None:
    # If both inputs are ints
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    else:
        return None

def remove_es(p_input : str = None) -> str | None:
    if isinstance(p_input, str):
        new_string : str = p_input.replace('e', '')
        return new_string
    else:
        return None