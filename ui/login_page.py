from core.safe_step import step
from playwright.sync_api import expect
from core.config import CONFIG
from ui.base_page import BasePage

class LoginPage(BasePage):
    @property
    def form(self):
        return self.page.locator('form:has(input[type=password]:visible):visible')

    @property
    def email(self):
        from ui.base_element import BaseElement
        return BaseElement(self.form.locator('input:not([type=hidden]):not([type=password]):not([type=submit]):not([type=checkbox]):not([type=button]):visible'), 'Email')

    @property
    def password(self):
        from ui.base_element import BaseElement
        return BaseElement(self.form.locator('input[type=password]:visible'), 'Пароль')

    @step('Открыть форму авторизации')
    def start(self):
        self.open(CONFIG.auth_path)
        self.password.visible()
        self.check_captcha()

    def login(self, email, password):
        self.email.fill(email)
        self.password.fill(password)
        self.form.locator('button[type=submit]:visible, input[type=submit]:visible, button:visible:text-is("Вход")').click()

    @step('Проверить отсутствие авторизации')
    def assert_rejected(self, expected):
        if expected in ('email_required', 'password_required'):
            field = self.email if expected == 'email_required' else self.password
            assert field.locator.evaluate('(el) => el.validity.valueMissing'), 'Не сработала проверка обязательного поля'
            assert field.locator.evaluate('(el) => el.validationMessage.length > 0'), 'Нет сообщения браузера'
        elif expected == 'invalid_format' and self.email.locator.evaluate('(el) => el.validity.typeMismatch'):
            assert self.email.locator.evaluate('(el) => el.validationMessage.length > 0'), 'Нет сообщения браузера'
        else:
            expect(self.page.locator(':text-is("Неверный логин или пароль"):visible')).to_be_visible()
        self.check_captcha()
        self.open(CONFIG.profile_path)
        self.password.visible()

    @step('Проверить сессию нужного пользователя')
    def assert_authenticated(self):
        expect(self.page.locator('input[type=password]:visible')).to_have_count(0)
        self.open(CONFIG.profile_path)
        # Сопоставление без вывода значения в assertion/Allure.
        self.page.wait_for_function('email => Array.from(document.querySelectorAll("input")).some(e => e.value.toLowerCase() === email.toLowerCase()) || document.body.innerText.toLowerCase().includes(email.toLowerCase())', arg=CONFIG.email)
        expect(self.page.locator('input[type=password]:visible')).to_have_count(0)
        self.check_captcha()
