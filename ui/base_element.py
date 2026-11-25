from playwright.sync_api import expect
from core.logger import log

class BaseElement:
    def __init__(self, locator, name):
        self.locator = locator
        self.name = name

    def click(self):
        log.info('Нажатие: %s', self.name)
        self.locator.click()

    def fill(self, value):
        log.info('Заполнение: %s (значение скрыто)', self.name)
        self.locator.fill(value)

    def visible(self):
        log.debug('Ожидание видимости: %s', self.name)
        expect(self.locator).to_be_visible()

    def text(self):
        self.visible()
        return self.locator.inner_text()
