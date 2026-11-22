from tickets import price


def test_a_child_pays_half_price():
    assert price(5) == 10


def test_an_adult_pays_full_price():
    assert price(30) == 20
