from main import valid_date


def test_valid_date_formats():
    assert valid_date("2023-12-31") == "2023-12-31"
    assert valid_date("31.12.2023") == "2023-12-31"


def test_invalid_date():
    assert valid_date("invalid") is None
    assert valid_date(None) is None
