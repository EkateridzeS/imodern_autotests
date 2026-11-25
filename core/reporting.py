import allure
from core.logger import log
from core.config import CONFIG


def attach_screenshot(page, title='Скриншот'):
    try:
        if page.is_closed():
            return

        masks = [
            page.locator(
                'input, textarea, [contenteditable], '
                'iframe, header, footer, canvas, img, svg'
            )
        ]

        for value in [
            CONFIG.email,
            CONFIG.password,
            CONFIG.name,
            CONFIG.phone
        ]:
            if value:
                masks.append(
                    page.get_by_text(value, exact=False)
                )

        screenshot = page.screenshot(
            full_page=True,
            mask=masks,
            mask_color="#000000",
            animations="disabled",
            timeout=10000
        )

        allure.attach(
            screenshot,
            name=title,
            attachment_type=allure.attachment_type.PNG
        )

        log.info('Скриншот прикреплен к Allure')

    except Exception:
        log.warning('Не удалось создать скриншот')


def attach_failure(page):
    attach_screenshot(page, 'Скриншот при ошибке')