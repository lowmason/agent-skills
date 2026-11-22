def split(total_cents: int, people: int) -> list[int]:
    share, left_over = divmod(total_cents, people)
    return [share + left_over if person == 0 else share for person in range(people)]
