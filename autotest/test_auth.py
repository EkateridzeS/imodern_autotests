import pytest
import allure
from core.safe_step import safe_step
from core.config import DATA
from core.logger import log
from ui.login_page import LoginPage

@pytest.mark.parametrize('case', DATA['auth'], ids=[c['id'] for c in DATA['auth']])
def test_auth(app_page, credentials, case):
    allure.dynamic.title(case['id'] + ': ' + case['title'])
    allure.dynamic.label('case_id', case['id'])
    allure.dynamic.parameter('Тип идентификатора', 'email')
    log.info('Начало %s', case['id'])
    emails = {'valid': credentials.email, 'empty': '', 'malformed': 'test@', 'unknown': 'test12345@example.com'}
    passwords = {'valid': credentials.password, 'empty': '', 'wrong': 'WrongPass123' if credentials.password != 'WrongPass123' else 'WrongPass456'}
    login = LoginPage(app_page)
    login.start()
    with safe_step('Ввести email и пароль (значения скрыты)'):
        login.login(emails[case['email']], passwords[case['password']])
    if case['expected'] == 'success':
        login.assert_authenticated()
    else:
        login.assert_rejected(case['expected'])
    log.info('Завершено %s', case['id'])
