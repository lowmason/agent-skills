FULL_PRICE = 20
CHILD_UNDER = 12
SENIOR_FROM = 65


def price(age: int) -> int:
    if age < CHILD_UNDER or age >= SENIOR_FROM:
        return FULL_PRICE // 2
    return FULL_PRICE
