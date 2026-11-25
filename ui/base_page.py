from playwright.sync_api import expect
from core.config import CONFIG
from ui.base_element import BaseElement

class BasePage:
    def __init__(self, page):
        self.page = page

    def open(self, path):
        self.page.goto(CONFIG.base_url + path, wait_until='domcontentloaded')
        self.check_captcha()

    def element(self, selector, name):
        return BaseElement(self.page.locator(selector), name)

    def control(self, text):
        # CSS Playwright с текстовым фильтром, не XPath по позиции.
        return self.element(f'button:visible:text-is("{text}"), a:visible:text-is("{text}"), input[type=submit][value="{text}"]:visible', text)

    def check_captcha(self):
        captcha = self.page.locator('iframe[src*="captcha"], [class*="smart-captcha"], [class*="g-recaptcha"], [class*="h-captcha"], script[src*="recaptcha"], script[src*="smartcaptcha"]')
        if captcha.count():
            raise AssertionError('Обнаружены признаки CAPTCHA: остановка теста, требуется замена сайта или согласование.')
