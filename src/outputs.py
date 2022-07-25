import csv
import logging

from datetime import datetime as dt
from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def build_table(result, trigger):
    if trigger.output == "pretty":
        table = PrettyTable()
        table.field_names = result[1]
        table.align = 'l'
        table.add_rows(result[2:])

        results_dir = BASE_DIR / "files" / "md"
        results_dir.mkdir(parents=True, exist_ok=True)
        file_name = result[0] + ".md"
        file_path = results_dir / file_name

        with open(file_path, encoding="utf-8", mode="w") as file:
            file.write(str(table))
        logging.info(f"Файл (.md) с результатами был сохранён: {file_path}")
    elif trigger.output == "table":
        results_dir = BASE_DIR / "files" / "csv"
        results_dir.mkdir(parents=True, exist_ok=True)

        now = dt.now().strftime(DATETIME_FORMAT)
        file_name = f"{result[0]}_{now}.csv"
        file_path = results_dir / file_name
        with open(file_path, encoding="utf-8", mode="w") as file:
            writer = csv.writer(file, dialect="unix", delimiter=";")
            writer.writerows(result[1:])
        logging.info(f"Файл (.csv) с результатами был сохранён: {file_path}")
    else:
        for row in result:
            print(*row)
