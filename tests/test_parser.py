import pytest
from main import Parser
from io import StringIO

VALID_LINE = '{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 0.024, "http_user_agent": "..."}'
INVALID_LINE = '{"@timestamp": "2025-06-22T13:57:32+00:00", "status"'


def test_parser_valid_json():
    f = StringIO(VALID_LINE)
    parser = Parser(files=[f], date=None, keywords=['url'], force=False)
    parser.parse()
    assert parser.out_dict != {}


def test_parser_invalid_json_with_force():
    f = StringIO(INVALID_LINE)
    parser = Parser(files=[f], date=None, keywords=['url'], force=True)
    parser.parse()
    assert parser.out_dict == {}


def test_parser_invalid_json_without_force():
    f = StringIO(INVALID_LINE)
    parser = Parser(files=[f], date=None, keywords=['url'], force=False)
    with pytest.raises(ValueError):
        parser.parse()


def test_parser_invalid_keyword_without_force():
    f = StringIO(VALID_LINE)
    with pytest.raises(ValueError):
        Parser(files=[f], date=None, keywords=['wrong_key'], force=False)


def test_parser_filter_by_date_blocks():
    f = StringIO(VALID_LINE)
    parser = Parser(files=[f], date="2023-01-01", keywords=['url'], force=False)
    parser.parse()
    assert parser.out_dict == {}
