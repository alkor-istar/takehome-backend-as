def escape_like(value: str, escape_char: str = "\\") -> str:
    # Escape the escape char first, then the LIKE wildcards
    value = value.replace(escape_char, escape_char + escape_char)
    value = value.replace("%", escape_char + "%")
    value = value.replace("_", escape_char + "_")
    return value
