import logging
import os
from core.config import ROOT, CONFIG


class RedactFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()

        secrets = [
            CONFIG.email,
            CONFIG.password,
            CONFIG.name,
            CONFIG.phone
        ]

        for secret in secrets:
            if secret:
                message = message.replace(
                    str(secret), '[REDACTED]'
                )

        record.msg = message
        record.args = ()

        return True


def setup_logger():
    logger = logging.getLogger('imodern')
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO').upper())
    logger.propagate = False

    if not logger.handlers:
        (ROOT / 'logs').mkdir(exist_ok=True)

        fmt = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        )

        for handler in (
            logging.StreamHandler(),
            logging.FileHandler(
                ROOT / 'logs/run.log',
                encoding='utf-8'
            )
        ):
            handler.setFormatter(fmt)
            handler.addFilter(RedactFilter())
            logger.addHandler(handler)

    return logger


log = setup_logger()