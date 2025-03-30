import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

async def save_session():
    user_data_dir = "user_data"
    logger.info("Запуск процедуры сохранения сессии WhatsApp Web")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = browser.pages[0] if browser.pages else await browser.new_page()
        logger.info("Открытие https://web.whatsapp.com")
        await page.goto("https://web.whatsapp.com")
        input("Нажмите Enter после входа в аккаунт и завершения авторизации в браузере...")
        await browser.close()
        logger.info("Сессия сохранена и браузер закрыт.")