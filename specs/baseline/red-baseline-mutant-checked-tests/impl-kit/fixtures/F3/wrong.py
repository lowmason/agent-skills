def count_words(text: str) -> int:
    total = 0
    for line in text.splitlines():
        if line.startswith('#'):
            continue
        total += len(line.split())
    return total
