import hashlib

def hashed_as_strings(*items):
    tokens = "|".join(list(map(str, items)))
    m = hashlib.sha256()
    m.update(tokens.encode(encoding="utf-8"))
    return m.digest().hex()
