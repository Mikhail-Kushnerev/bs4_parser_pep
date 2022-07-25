import csv
import logging

from datetime import datetime as dt
from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(result):
    table = PrettyTable()
    table.field_names = result[0]
    table.align = 'l'
    table.add_rows(result[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(exist_ok=True)

    name_table = cli_args.mode
    now = dt.now().strftime(DATETIME_FORMAT)
    file_name = f"{name_table}_{now}.csv"
    file_path = results_dir / file_name
    with open(file_path, encoding="utf-8", mode="w") as file:
        writer = csv.writer(file, dialect="unix", delimiter=";")
        writer.writerows(results)
    logging.info(f"Файл (.csv) с результатами был сохранён: {file_path}")
