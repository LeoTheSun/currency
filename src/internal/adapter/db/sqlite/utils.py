from re import compile


def format_query(query: str) -> str:
    space = compile('\s+')
    return ' '.join(space.split(query)).strip()