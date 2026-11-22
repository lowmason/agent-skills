from loyalty import points


def test_double_points_from_100_dollars():
    assert points(15000) == 300
