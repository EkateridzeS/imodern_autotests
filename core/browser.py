from core.config import CONFIG
from core.logger import log

def new_context(browser):
    context = browser.new_context(locale='ru-RU', viewport={'width': 1440, 'height': 1000})
    context.set_default_timeout(CONFIG.timeout)
    context.set_default_navigation_timeout(CONFIG.timeout)
    log.debug('Создан изолированный контекст браузера')
    return context
