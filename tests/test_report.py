import pytest
from main import Report


def get_dummy_out_dict():
    return {('url_1',): [5, 500]}


def test_report_stdout_output(capsys):
    report = Report(outfile=None,
                    keywords=["url"],
                    report="average",
                    force=True,
                    out_dict=get_dummy_out_dict())
    report.out_parsing_data()
    captured = capsys.readouterr()
    assert "url_1" in captured.out
    assert "avg_response_time" in captured.out


def test_report_file_output(tmp_path):
    out_file = tmp_path / "report.txt"
    with out_file.open("w") as f:
        report = Report(outfile=f,
                        keywords=["url"],
                        report="average",
                        force=True,
                        out_dict=get_dummy_out_dict())
        report.out_parsing_data()

    content = out_file.read_text()
    assert "url_1" in content


def test_report_no_data_raises():
    with pytest.raises(ValueError, match="Нет статистики"):
        report = Report(outfile=None,
                        keywords=["url"],
                        report="average",
                        force=False,
                        out_dict={})
        report.out_parsing_data()


def test_report_no_keywords_raises():
    with pytest.raises(ValueError, match="Не указаны ключевые"):
        report = Report(outfile=None,
                        keywords=[],
                        report="average",
                        force=False,
                        out_dict={("a",): [1, 100]})
        report.out_parsing_data()


def test_report_wrong_type_raises():
    with pytest.raises(ValueError, match="Скрипт умеет только вариант отчёта"):
        report = Report(outfile=None,
                        keywords=["url"],
                        report="min",
                        force=False,
                        out_dict={("a",): [1, 100]})
        report.out_parsing_data()
