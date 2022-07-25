import argparse
import logging

from logging.handlers import RotatingFileHandler
from constants import (
    BASE_DIR,
    DT_FORMAT,
    LOG_FORMAT
)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        "-c",
        "--clear_cache",
        action="store_true",
        help="Очистка кэша"
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=("pretty", "file"),
        help="Построение таблицы"
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "parser.log"
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=pow(10, 6), backupCount=5
    )
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DT_FORMAT,
        handlers=(rotating_handler, logging.StreamHandler())
    )
