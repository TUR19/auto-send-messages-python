import asyncio
import logging
from threading import Timer
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, timeout: int = 1800):
        self.timeout = timeout
        self.timer = None
        self.browser_context = None
        self.playwright = None

    async def start_browser(self, user_data_dir: str):
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser_context:
            self.browser_context = await self.playwright.chromium.launch_persistent_context(user_data_dir, headless=False)
        return self.browser_context

    async def stop_browser(self):
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    def reset_timer(self):
        if self.timer:
            self.timer.cancel()
        loop = asyncio.get_event_loop()
        self.timer = Timer(self.timeout, lambda: asyncio.run_coroutine_threadsafe(self.stop_browser(), loop))
        self.timer.start()

    def is_browser_running(self):
        return self.browser_context is not None

from app.session import save_session
import os

async def check_user_data_dir(user_data_dir: str):
    if not os.path.exists(user_data_dir):
        await save_session()

browser_manager = BrowserManager()