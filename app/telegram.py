import logging
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

async def send_message_telegram(browser_context: BrowserContext, phone_number: str, message: str):
    logger.info(f"Отправка сообщения. Номер: {phone_number}")
    page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

    # if "web.whatsapp.com" not in page.url:
    if not page.url.startswith("https://web.telegram.org/k"):
        await page.goto("https://web.telegram.org/k/")
        await page.wait_for_timeout(5000)
        logger.info("Страница Telegram Web загружена.")

    logger.info(f"Поиск контакта по номеру: {phone_number}")
    # search_input = page.locator('xpath=//span[contains(text(), "оиск")]')
    search_input = page.locator('xpath=//div[@class="input-search"]//input')
    await search_input.click()
    await search_input.fill(phone_number)
    await page.wait_for_timeout(3000)

    contact = page.locator('xpath=(//span[contains(text(), "Чаты")]/parent::div/following-sibling::ul//div)[1]')
    await contact.wait_for(timeout=10000)
    await contact.click()
    logger.info("Контакт найден. Открыт чат.")

    msg_input = page.locator('xpath=(//div[@class="input-message-container"]//div)[1]')
    await msg_input.wait_for(timeout=10000)
    await msg_input.click()
    await msg_input.fill(message)
    await msg_input.press("Enter")