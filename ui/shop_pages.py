import re
from core.safe_step import step
from playwright.sync_api import expect
from ui.base_page import BasePage
from core.config import CONFIG


def money(text):
    match = re.search(r'\d[\d\s\u00a0\u202f]*', text)
    assert match, 'Цена не найдена'
    return int(re.sub(r'\D', '', match.group()))

class ShopPage(BasePage):
    @step('Поиск товара и переход в карточку')
    def search_product(self, product):
        search = self.element(
            'input[placeholder="Введите запрос"]:visible',
            'Поиск'
        )

        search.fill(product['query'])
        search.locator.press('Enter')

        link = self.page.locator(
            f'a[href*="{product["path"]}"]:visible'
        ).first

        link.wait_for(state='visible', timeout=30000)
        link.click()

        expect(self.page.locator('h1')).to_contain_text(
            re.compile(re.escape(product['name']), re.I)
        )

        expect(self.page.locator('body')).to_contain_text(
            product['code']
        )

        self.check_captcha()

    @step('Получить цену и добавить товар в корзину')
    def add_product(self):
        from core.logger import log

        self.page.wait_for_load_state('load')

        buy = self.page.get_by_text(
            re.compile(r'^Добавить в корзину$', re.I)
        ).filter(visible=True)

        expect(buy).to_be_visible(timeout=30000)

        price_locator = self.page.get_by_text(
            re.compile(r'^11\s*880\s*(₽|руб\.?)?$')
        ).filter(visible=True).first

        expect(price_locator).to_be_visible(timeout=30000)

        price = money(price_locator.inner_text())

        log.info('Цена товара: %s рублей', price)

        buy.click()

        log.info('Нажата кнопка добавления товара в корзину')

        self.check_captcha()

        return price

class CartPage(BasePage):
    def open_cart(self):
        self.open('/cart/')
        expect(self.page.locator('h1')).to_contain_text(
            re.compile('корзина', re.I)
        )
        self.check_captcha()

    @step('Очистить корзину тестового аккаунта')
    def clear(self):
        # Не удаляем данные незнакомого аккаунта: используются только выделенные тестовые данные.
        delete = self.page.locator('[title*="Удалить"]:visible, [aria-label*="Удалить"]:visible, button[class*="delete"]:visible, a[class*="delete"]:visible')
        for _ in range(30):
            count = delete.count()
            if not count:
                break
            delete.first.click()
            expect(delete).to_have_count(count - 1)
        expect(self.page.locator('body')).to_contain_text(re.compile('корзина пуста|ничего не добавили|нет товаров|корзине нет', re.I))

    @step('Проверить товар, количество и сумму')
    def verify(self, product, price):
        from core.logger import log
        log.info('Проверка названия товара')
        expect(self.page.locator('body')).to_contain_text(
            product['name']
        )
        log.info('Название товара совпадает')
        qty = self.page.get_by_role("main").get_by_text(
            str(product['quantity']),
            exact=True
        )
        expect(qty).to_be_visible()
        log.info('Количество товара совпадает')
        log.info('Проверка итоговой стоимости')
        self.verify_total(price * product['quantity'])
        log.info('Итоговая стоимость совпадает')

    def verify_total(self, total):
        label = self.page.locator(':text-is("Итого к оплате:"):visible')
        expect(label).to_be_visible()
        actual = label.locator('xpath=..').inner_text()
        assert money(actual) == total, 'Итоговая сумма не совпадает'

    @step('Проверить контактные данные и перейти к доставке')
    def contacts(self, comment):
        from core.logger import log

        self.control('Оформить заказ').click()

        self.page.wait_for_url(
            '**/order/',
            timeout=30000
        )

        self.page.wait_for_load_state(
            'load',
            timeout=90000
        )

        log.info('Страница оформления полностью загружена')

        name = self.page.locator('label').filter(
            has_text='Фамилия, Имя*'
        ).locator('input')

        phone = self.page.locator('label').filter(
            has_text='Номер телефона'
        ).locator('input')

        email = self.page.locator('label').filter(
            has_text='E-mail'
        ).locator('input')

        expect(name).to_be_visible()

        assert name.input_value().strip() == CONFIG.name, \
            'Имя не совпадает'

        log.info('Имя заполнено корректно')

        actual_phone = re.sub(r'\D', '', phone.input_value())
        expected_phone = re.sub(r'\D', '', CONFIG.phone)

        assert actual_phone[-10:] == expected_phone[-10:], \
            'Телефон не совпадает'

        log.info('Телефон заполнен корректно')

        assert email.input_value().lower() == CONFIG.email.lower(), \
            'Email не совпадает'

        log.info('Email заполнен корректно')

        log.info('Начало заполнения комментария')

        self.element(
            'textarea:visible',
            'Комментарий'
        ).fill(comment)

        log.info('Комментарий успешно заполнен')

        self.page.locator('textarea:visible').press('Tab')

        button = self.page.get_by_text(
            "ПРОДОЛЖИТЬ ОФОРМЛЕНИЕ",
            exact=True
        )

        expect(button).to_be_visible(timeout=30000)
        expect(button).to_be_enabled(timeout=30000)

        button.scroll_into_view_if_needed()

        log.info('Переход к оформлению доставки')
        self.page.wait_for_load_state(
            'networkidle',
            timeout=30000
        )

        with self.page.expect_response(
                lambda response:
                '/local/ajax/order3.php' in response.url
                and response.request.method == 'POST',
                timeout=90000
        ) as response_info:
            button.click()

        response = response_info.value

        log.info(
            'Ответ сервера оформления: HTTP %s',
            response.status
        )

        assert response.status == 200, (
            f'Ошибка сервера оформления: HTTP {response.status}'
        )

        expect(self.page.get_by_text(
            'Забрать с нашего склада',
            exact=True
        ).filter(visible=True)).to_be_visible(timeout=30000)

        log.info('Форма доставки успешно открылась')

        self.check_captcha()

    @step('Выбрать самовывоз и оплату при получении')
    def delivery(self):
        from core.logger import log

        pickup = self.page.get_by_text(
            'Забрать с нашего склада',
            exact=True
        ).filter(visible=True)

        expect(pickup).to_be_visible(timeout=30000)
        pickup.click()

        log.info('Нажат вариант самовывоза')

        payment = self.page.get_by_text(
            'Оплата при получении',
            exact=True
        ).filter(visible=True)

        expect(payment).to_be_visible(timeout=30000)
        payment.click()

        log.info('Нажат вариант оплаты при получении')

        pickup_input = pickup.locator(
            'xpath=ancestor::label[1]'
        ).locator('input')

        payment_input = payment.locator(
            'xpath=ancestor::label[1]'
        ).locator('input')

        expect(pickup_input).to_be_checked()
        log.info('Выбор самовывоза подтвержден')

        expect(payment_input).to_be_checked()
        log.info('Выбор оплаты при получении подтвержден')

        button = self.page.get_by_text(
            re.compile(r'^Оплатить заказ$', re.I)
        ).filter(visible=True)

        expect(button).to_be_visible(timeout=30000)

        log.info('Финальная кнопка доступна')

        self.check_captcha()

    @step('Создать заказ и проверить подтверждение')
    def submit_order(self, product, total):
        assert CONFIG.allow_order, 'Отправка заказа не разрешена'
        self.control('Оформить заказ').click()
        self.check_captcha()
        expect(self.page.locator('body')).to_contain_text(re.compile(r'(заказ оформлен|заказ создан|спасибо за заказ)', re.I))
        expect(self.page.locator('body')).to_contain_text(re.compile(r'(?:номер заказа|заказ\s*№)\s*[:№]?\s*\d+', re.I))
        expect(self.page.locator('body')).to_contain_text(product['name'])
        expect(self.page.locator('body')).to_contain_text(re.compile(r'\s*'.join(str(total))))
