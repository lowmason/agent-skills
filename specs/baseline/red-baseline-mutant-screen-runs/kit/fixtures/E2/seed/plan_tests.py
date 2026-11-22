from bills import split


def test_an_even_bill_splits_equally():
    assert split(900, 3) == [300, 300, 300]


def test_the_first_person_pays_the_cent_left_over():
    assert split(1000, 3) == [334, 333, 333]
