import pytest
import allure
from playwright.sync_api import sync_playwright
from core.config import CONFIG
from core.browser import new_context
from core.logger import log
from core.reporting import attach_screenshot

@pytest.fixture(scope='session')
def browser_instance():
    with sync_playwright() as p:
        browser = getattr(p, CONFIG.browser).launch(headless=CONFIG.headless)
        yield browser
        browser.close()

@pytest.fixture
def app_page(browser_instance):
    context = new_context(browser_instance)
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def credentials():
    if not CONFIG.email or not CONFIG.password:
        pytest.skip('Заполните TEST_EMAIL и TEST_PASSWORD в .env')
    return CONFIG

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        page = item.funcargs.get('app_page')

        if page:
            if report.failed:
                attach_screenshot(
                    page,
                    'Скриншот при ошибке'
                )

            elif report.passed:
                attach_screenshot(
                    page,
                    'Результат успешного теста'
                )

            elif report.skipped:
                attach_screenshot(
                    page,
                    'Состояние при остановке теста'
                )

        if report.failed:
            log.error('Ошибка в тесте %s', item.name)

            report.longrepr = (
                'Проверка не пройдена. '
                'См. безопасные шаги и диагностику Allure.'
            )