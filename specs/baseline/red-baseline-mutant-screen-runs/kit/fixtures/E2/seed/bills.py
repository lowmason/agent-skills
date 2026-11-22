def split(total_cents: int, people: int) -> list[int]:
    share, left_over = divmod(total_cents, people)
    return [share + 1 if person < left_over else share for person in range(people)]
