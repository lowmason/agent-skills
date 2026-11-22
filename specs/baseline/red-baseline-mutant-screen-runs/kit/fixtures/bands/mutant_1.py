SMALL_LIMIT = 500
MEDIUM_LIMIT = 2000


def is_large(grams: int) -> bool:
    return grams >= MEDIUM_LIMIT


def band(grams: int) -> str:
    if is_large(grams):
        return 'large'
    if grams >= SMALL_LIMIT:
        return 'medium'
    return 'small'
