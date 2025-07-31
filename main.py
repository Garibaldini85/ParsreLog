from typing import TextIO
import argparse
import json
from datetime import datetime
from tabulate import tabulate


class Parser:
    accepted_keywords_list = ['status', 'url', 'request_method', 'response_time', 'http_user_agent']

    def __init__(self, files: list, date: str = None,
                 keywords: list = None, force: bool = False):
        self._force = force
        self._files = files
        self._date = date
        self.keywords = None
        self._init_keywords_list(keywords)
        self.out_dict = {}

    def _init_keywords_list(self, keywords: list) -> None:
        if keywords is None:
            self.keywords = ['url']
            return

        self.keywords = []
        for keyword in keywords:
            if keyword in Parser.accepted_keywords_list:
                self.keywords.append(keyword)
            elif not self._force:
                raise ValueError(f"Недопустимое ключевое слово: {keyword}")

        if len(self.keywords) == 0:
            self.keywords = ['url']

    def _get_keywords(self, line: dict) -> tuple | None:
        try:
            return tuple(line[key] for key in self.keywords)
        except KeyError as e:
            if not self._force:
                raise KeyError(f"Missing key in input line: {e}")
            return None

    def _parse_line(self, line: str) -> None:
        try:
            json_obj = json.loads(line)
        except json.JSONDecodeError as e:
            if not self._force:
                raise ValueError(f"Невалидный JSON: {e}")
            return None

        if self._date is not None:
            timestamp = json_obj.get('@timestamp')
            if not timestamp or self._date not in timestamp:
                return None

        tuple_key = self._get_keywords(json_obj)
        item = self.out_dict.get(tuple_key)
        if item is None:
            self.out_dict[tuple_key] = [1, json_obj['response_time']]
        else:
            self.out_dict[tuple_key][0] += 1
            self.out_dict[tuple_key][1] += json_obj['response_time']

        return None

    def _parse_file(self, file: TextIO) -> None:
        for line in file:
            if line.strip():
                self._parse_line(line)

    def parse(self) -> None:
        self.out_dict = {}
        for file in self._files:
            self._parse_file(file)


def valid_date(s_date: str) -> str | None:
    if s_date is None:
        return None

    for template_date in ('%Y-%m-%d', '%d.%m.%Y'):
        try:
            return datetime.strptime(s_date, template_date).strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


class Report:
    def __init__(self, report: str, force: bool,
                 keywords: list, out_dict: dict,
                 outfile: TextIO = None) -> None:
        self._outfile = outfile
        self._keywords = keywords
        self._report = report
        self._force = force
        self._out_dict = out_dict

    def out_parsing_data(self):
        if not self._force and len(self._out_dict) == 0:
            raise ValueError("Нет статистики для вывода: входные данные не содержат подходящих записей.")

        if not self._force and len(self._keywords) == 0:
            raise ValueError("Не указаны ключевые слова для группировки: невозможно построить отчёт.")

        if not self._force and self._report != "average":
            raise ValueError("Скрипт умеет только вариант отчёта 'average'. Использование других вариантов запрещено.")

        body = []
        for key, (cnt, total_rt) in self._out_dict.items():
            avg = (total_rt / cnt) if cnt else 0.0
            body.append(list(key) + [cnt, avg])

        body = sorted(body, key=lambda x: x[-2], reverse=True)
        headers = self._keywords + ["total", "avg_response_time"]

        if self._outfile:
            self._outfile.write(tabulate(body, headers=headers))
            return

        print(tabulate(body, headers=headers))


def start_program():
    args_parser = argparse.ArgumentParser(description="Анализ логов и отчётов.")

    args_parser.add_argument("--file", required=True,
                             nargs='+', type=argparse.FileType('r'),
                             help="Путь к файлу логов")
    args_parser.add_argument("--report", choices=["average"], required=True,
                             help="Тип отчёта: average, можно расширить до max и min")
    args_parser.add_argument("--date", type=valid_date, help="Дата выборки логов")
    args_parser.add_argument("--keywords", nargs='*', type=str, help="Ключевые поля для анализа")
    args_parser.add_argument("--output", type=argparse.FileType('w'),
                             help="Путь к файлу отчета")
    args_parser.add_argument('--force', action='store_true', help='Игнорировать ошибки строк?')

    args = args_parser.parse_args()

    print(f"Файл: {', '.join((i.name for i in args.file))}")
    print(f"Тип отчёта: {args.report}")
    print(f"Дата выборки логов: {args.date if args.date else 'Не выбрана'}")
    print(f"Ключевые поля для анализа: {', '.join(args.keywords) if args.keywords else 'url'}")
    print(f"Игнорировать ошибки строк: {'Да' if args.force else 'Нет'}")
    print(f"Файл вывода: {args.output.name if args.output else 'Не выбран'}")

    parser = Parser(files=args.file, date=args.date,
                    keywords=args.keywords, force=args.force)
    parser.parse()

    report = Report(outfile=args.output, keywords=parser.keywords, report=args.report,
                    force=args.force, out_dict=parser.out_dict)
    report.out_parsing_data()


if __name__ == '__main__':
    start_program()
