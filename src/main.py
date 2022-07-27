import logging
import re
import requests_cache

from typing import Pattern
from urllib.parse import urljoin
from bs4 import BeautifulSoup as Bs
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    MAIN_DOC_URL,
    PEP,
    EXPECTED_STATUS,
    PATTERN
)
from outputs import control_output
from utils import get_response, find_tag, check_key


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = Bs(response.text, "lxml")
    section_tag = find_tag(
        soup,
        "section",
        attrs={"id": "what-s-new-in-python"}
    )
    div_tag = find_tag(
        section_tag, "div",
        attrs={"class": "toctree-wrapper compound"}
    )
    li_tag = div_tag.find_all("li", class_="toctree-l1")
    results = [
        ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')
    ]
    for i in tqdm(li_tag):
        a_tag = find_tag(i, "a")["href"]
        string = urljoin(whats_new_url, a_tag)

        response = get_response(session, string)
        if response is None:
            return
        soup = Bs(response.text, "lxml")
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (string, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = Bs(response.text, "lxml")

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in tqdm(ul_tags, desc="Поиск тэгов 'a'"):
        if "All versions" in ul.text:
            all_a_tags = ul.find_all("a")
            break
    else:
        raise Exception("Ничего не нашлось!")

    pattern = r"Python\s([\d\.]+)\s\((\w{1,}.*)\)"
    results = [
        ('Ссылка на документацию', 'Версия', 'Статус')
    ]
    for i in tqdm(all_a_tags, desc="Разбор содержимого тэга 'a'"):
        result = re.search(pattern, i.text)
        if result:
            version, status = result.groups()
        else:
            version, status = i.text, ''
        results.append(
            (i["href"], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = Bs(response.text, "lxml")
    main_role = find_tag(soup, "div", attrs={"role": "main"})
    table = find_tag(main_role, "table", attrs={"class": "docutils"})
    pattern: Pattern[str] = re.compile(r'.*pdf-a4\.zip$')
    a_tag = find_tag(table, "a", attrs={"href": pattern})
    pdf_link = a_tag["href"]

    download_link = urljoin(downloads_url, pdf_link)
    obj_name = download_link.split("/")[-1]

    downloads_dir = BASE_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    archive_path = downloads_dir / obj_name
    download = session.get(download_link)
    with open(archive_path, mode='wb') as file:
        file.write(download.content)
    logging.info(f"Архив был загружен и сохранён: {archive_path}")


def pep(session):
    response = get_response(session, PEP)
    if response is None:
        return

    soup = Bs(response.text, "lxml")
    section_tag = find_tag(soup, "section", attrs={"id": "numerical-index"})
    body_table = find_tag(section_tag, "tbody")
    rows = body_table.find_all("tr")

    counter = {}
    for string in rows:
        td_tag = find_tag(string, "td")
        href_object = td_tag.find_next_sibling("td")
        td_tag = td_tag.text
        link_object = urljoin(PEP, href_object.a["href"])
        response = get_response(session, link_object)
        if response is None:
            return

        soup = Bs(response.text, "lxml")
        start = find_tag(soup, text=PATTERN).parent
        dt = start.find_next_sibling("dd").text
        if len(td_tag) > 1 and check_key(td_tag[1]):
            if dt not in EXPECTED_STATUS[td_tag[1]]:
                error_msg = ''.join(
                    (
                        "\nНесовпадающие статусы:\n",
                        f"\t{link_object}\n",
                        f"\tСтатус в карточке: {dt}\n",
                        f"\tОжадиаемые статусы: {EXPECTED_STATUS[td_tag[1]]}"
                    )
                )
                logging.info(error_msg)
                continue
        counter[dt] = counter.get(dt, 0) + 1
    counter["Total"] = sum(i for i in counter.values())
    results = [
        ("Статус", "Количество")
    ]
    results.extend(counter.items())
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info("Парсер запущен")

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == "__main__":
    main()
