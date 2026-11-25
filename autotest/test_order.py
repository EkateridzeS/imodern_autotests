import allure
import pytest

from core.safe_step import safe_step
from core.config import DATA
from core.logger import log
from ui.login_page import LoginPage
from ui.shop_pages import ShopPage, CartPage


@pytest.mark.e2e
@allure.title('TK-E2E-01: Поиск, корзина и оформление заказа')
def test_order(app_page, credentials):
    allure.dynamic.label('case_id', 'TK-E2E-01')

    if not credentials.name or not credentials.phone:
        pytest.skip('Заполните TEST_NAME и TEST_PHONE в .env')

    product = DATA['product']

    login = LoginPage(app_page)
    login.start()

    with safe_step('Войти в тестовый аккаунт'):
        login.login(credentials.email, credentials.password)

    login.assert_authenticated()

    cart = CartPage(app_page)

    with safe_step('Открыть корзину перед тестированием'):
        cart.open_cart()

    cart.clear()

    shop = ShopPage(app_page)
    shop.search_product(product)
    price = shop.add_product()

    with safe_step('Перейти в корзину после добавления товара'):
        cart.open_cart()

    cart.verify(product, price)
    cart.contacts(product['comment'])
    cart.delivery()

    with safe_step('Проверить итоговую стоимость заказа'):
        cart.verify_total(price * product['quantity'])

    if not credentials.allow_order:
        log.warning('Финальная отправка отключена')
        pytest.skip('Создание заказа не согласовано')

    cart.submit_order(product, price * product['quantity'])