import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        logging.exception(
            f"Возникла ошибка при загрузке страницы {url}",
            stack_info=True
        )


def find_tag(soup, tag=None, attrs=None, text=None):
    if text:
        searched_tag = soup.find(text=text)
        if searched_tag is None:
            error_msg = f"Тэг, имеющий текст '{text}' не найден"
            logging.error(error_msg, stack_info=True)
            raise ParserFindTagException(error_msg)
    else:
        searched_tag = soup.find(tag, attrs=(attrs or {}))
        if searched_tag is None:
            error_msg = f"Не найден тэг '{tag}' с параметрами: '{attrs}'"
            logging.error(error_msg, stack_info=True)
            raise ParserFindTagException(error_msg)
    return searched_tag
