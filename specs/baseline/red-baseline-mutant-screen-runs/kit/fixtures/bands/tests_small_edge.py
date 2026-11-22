from bands import band


def test_band_small():
    assert band(100) == 'small'


def test_band_medium():
    assert band(1200) == 'medium'


def test_band_large():
    assert band(5000) == 'large'


def test_band_small_at_its_upper_edge():
    assert band(500) == 'small'
