import asyncio
import logging
from threading import Timer
from playwright.async_api import async_playwright
from app.session import save_session
import os

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, timeout: int = 1800):
        self.timeout = timeout
        self.timer = None
        self.browser_context = None
        self.playwright = None

    async def start_browser(self, user_data_dir: str):
        logger.info("Инициализация запуска браузера...")
        if not self.playwright:
            logger.info("Playwright ещё не запущен. Запускаем...")
            self.playwright = await async_playwright().start()
        if not self.browser_context:
            logger.info("Создание нового браузерного контекста...")
            self.browser_context = await self.playwright.chromium.launch_persistent_context(user_data_dir, headless=False)
        logger.info(f"Запуск браузера с user_data_dir: {user_data_dir}")
        return self.browser_context
    
    async def stop_browser(self):
        logger.info("Остановка браузера")
        if self.browser_context:
            try:
                await self.browser_context.close()
            except Exception as e:
                logger.warning(f"Ошибка при закрытии браузера: {e}")
            self.browser_context = None

        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Ошибка при остановке Playwright: {e}")
            self.playwright = None

    def reset_timer(self):
        logger.info(f"Сброс таймера на {self.timeout} секунд.")
        if self.timer:
            self.timer.cancel()
        loop = asyncio.get_event_loop()
        self.timer = Timer(self.timeout, lambda: asyncio.run_coroutine_threadsafe(self.stop_browser(), loop))
        self.timer.start()

    def is_browser_running(self):
        # return self.browser_context is not None and not self.browser_context.is_closed()
        if self.browser_context is None:
            return False
        try:
            _ = self.browser_context.pages  # доступ безопасен
            return True
        except Exception as e:
            logger.warning(f"Контекст закрыт или недоступен: {e}")
            return False

    async def ensure_browser(self, user_data_dir: str):
        restart_needed = False
        
        if self.browser_context is None:
            restart_needed = True
        else:
            try:
                _ = await self.browser_context.new_page()
            except Exception as e:
                logger.warning(f"Контекст не работает. Причина: {e}")
                restart_needed = True

        if restart_needed:
            logger.info("Запуск браузера")
            await self.stop_browser()
            await self.start_browser(user_data_dir)


async def check_user_data_dir(user_data_dir: str):
    logger.info("Проверка наличия user_data_dir: %s", user_data_dir)
    if not os.path.exists(user_data_dir):
        logger.info("user_data_dir не найден. Запуск save_session()")
        await save_session()

browser_manager = BrowserManager()