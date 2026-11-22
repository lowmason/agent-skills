CENTS_PER_DOLLAR = 100
DOUBLE_FROM_CENTS = 10000


def points(cents: int) -> int:
    dollars = cents // CENTS_PER_DOLLAR
    if cents >= DOUBLE_FROM_CENTS:
        return dollars * 2
    return dollars
