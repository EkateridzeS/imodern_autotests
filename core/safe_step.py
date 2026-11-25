import re
from contextlib import contextmanager
from functools import wraps

import allure
from core.logger import log


@contextmanager
def safe_step(title):
    with allure.step(title):
        try:
            yield

        except Exception as exc:
            error_type = type(exc).__name__
            message = f'Сбой шага: {title} ({error_type})'

            http_code = re.search(
                r'Ошибка сервера оформления: HTTP (\d{3})',
                str(exc)
            )

            network_code = re.search(
                r'net::ERR_[A-Z0-9_]+',
                str(exc)
            )

            if http_code:
                message += (
                    f'. Ошибка сервера: HTTP {http_code.group(1)}'
                )

            elif network_code:
                message += (
                    f'. Ошибка подключения: {network_code.group()}'
                )

            elif 'Timeout' in error_type:
                message += '. Превышено время ожидания'

            log.error(message)

            allure.attach(
                message,
                name='Причина ошибки',
                attachment_type=allure.attachment_type.TEXT
            )

            raise AssertionError(message) from None


def step(title):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            with safe_step(title):
                return fn(*args, **kwargs)
        return wrapped
    return decorate