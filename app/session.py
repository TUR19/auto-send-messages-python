import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

async def save_session():
    user_data_dir = "user_data"
    async with async_playwright() as p:
        logger.info("Запуск процедуры сохранения сессии (WhatsApp Web и Telegram Web)")
        browser = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = browser.pages[0] if browser.pages else await browser.new_page()
        logger.info("Открытие https://web.whatsapp.com")
        await page.goto("https://web.whatsapp.com")
        input("Нажмите Enter после входа в аккаунт и завершения авторизации в WhatsApp Web")
        
        logger.info("Открытие https://web.telegram.org/k/")
        await page.goto("https://web.telegram.org/k/")
        input("Нажмите Enter после входа в аккаунт и завершения авторизации в Telegram Web")
        await browser.close()
        logger.info("Сессия сохранена и браузер закрыт.")