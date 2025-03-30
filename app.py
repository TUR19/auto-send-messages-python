import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from save_session import save_session
from threading import Timer
# from prometheus_client import Counter, Histogram, start_http_server
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

USER_DATA_DIR = "user_data"

# # Метрики Prometheus
# REQUEST_COUNT = Counter("api_requests_total", "Total number of API requests", ["method", "endpoint"])
# REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Latency of API requests", ["endpoint"])

# Инициализация FastAPI приложения
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await check_user_data_dir(USER_DATA_DIR)

class BrowserManager:
    def __init__(self, timeout: int):
        # Инициализация менеджера браузера с таймаутом
        self.timeout = timeout
        self.timer = None
        self.browser_context = None
        self.playwright = None
        logger.info("BrowserManager инициализирован с таймаутом: %d секунд", timeout)

    async def start_browser(self, user_data_dir: str):
        # Запуск Playwright, если он еще не был запущен
        logger.debug("Инициализация браузера. user_data_dir=%s", user_data_dir)
        if not self.playwright:
            logger.info("Запуск Playwright...")
            self.playwright = await async_playwright().start()
        # Запуск браузера с указанной папкой пользовательских данных
        if not self.browser_context:
            logger.info("Запуск браузера с user_data_dir: %s", user_data_dir)
            self.browser_context = await self.playwright.chromium.launch_persistent_context(user_data_dir, headless=False)
        logger.debug("Браузер успешно запущен.")
        return self.browser_context

    async def stop_browser(self):
        # Закрытие браузера и остановка Playwright
        logger.info("Закрытие браузера...")
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.debug("Браузер успешно закрыт.")

    def reset_timer(self):
        # Сброс таймера для автоматического закрытия браузера
        logger.info("Сброс таймера на %d секунд.", self.timeout)
        if self.timer:
            self.timer.cancel()
        loop = asyncio.get_event_loop()
        self.timer = Timer(self.timeout, lambda: asyncio.run_coroutine_threadsafe(self.stop_browser(), loop))
        self.timer.start()
        logger.debug("Таймер перезапущен.")

    def is_browser_running(self):
        # Проверка, работает ли браузер в данный момент
        logger.debug("Проверка состояния браузера. Работает: %s", self.browser_context is not None)
        return self.browser_context is not None

# Экземпляр BrowserManager с таймаутом 30 минут
browser_manager = BrowserManager(timeout=1800)

async def check_user_data_dir(user_data_dir: str):
    # Проверка существования папки пользовательских данных
    logger.debug("Проверка существования user_data_dir: %s", user_data_dir)
    if not os.path.exists(user_data_dir):
        logger.info("Папка user_data не найдена. Сохраняем сессию...")
        await save_session()
    else:
        logger.info("Папка user_data найдена: %s", user_data_dir)

async def send_message(browser_context, phone_number: str, message: str):
    # Отправка сообщения через WhatsApp Web
    logger.debug("Инициализация отправки сообщения. Номер: %s, Сообщение: %s", phone_number, message)
    page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

    try:
        # Проверка, открыт ли WhatsApp Web
        if "web.whatsapp.com" not in page.url:
            logger.info("Переход на WhatsApp Web...")
            await page.goto("https://web.whatsapp.com")
            
        # async with page.expect_response(lambda response: "https://graph.whatsapp.net/wa_qpl_data" in response.url and response.status == 200):
        #     logger.info("Ожидание загрузки WhatsApp Web через сетевой запрос...")
        #     # await page.goto("https://web.whatsapp.com")
            
        #     # Ждем появления поля поиска после загрузки WhatsApp
        #     await page.wait_for_selector('xpath=//div[contains(text(),"Поиск")]', state="visible", timeout=30000)
        # logger.info("WhatsApp Web полностью загружен.")


        # Очистка строки поиска, если это необходимо
        clear_search_data = page.locator('xpath=//button[contains(text(),"Отменить поиск")]')
        if await clear_search_data.is_visible():
            logger.debug("Очистка строки поиска...")
            await clear_search_data.click()

        # Поиск контакта по номеру телефона
        logger.info("Поиск контакта. Номер: %s", phone_number)
        search_input = page.locator('xpath=//div[contains(@aria-label, "поиск")]')
        await search_input.click()
        await search_input.fill(phone_number)
        await page.wait_for_timeout(5000)

        # Выбор найденного контакта
        search_client = page.locator('xpath=//div[contains(text(), "Чаты")]/parent::div/following-sibling::div[1]')
        await search_client.click()

        # Логирование отправляемого сообщения
        logger.info("Отправка сообщения: Номер: %s, Сообщение: %s", phone_number, message)

        # Ввод сообщения и отправка
        msg_input = page.locator('xpath=//div[@aria-label="Введите сообщение"]')
        await msg_input.click()
        await msg_input.fill(message)
        await msg_input.press("Enter")

        # Ожидание завершения отправки
        logger.debug("Сообщение отправлено. Ожидание завершения...")
        await page.wait_for_timeout(5000)
    except Exception as e:
        logger.error("Произошла ошибка при отправке сообщения: %s", e)
        raise Exception(f"Произошла ошибка: {e}")

class MessageRequest(BaseModel):
    # Модель данных для запроса отправки сообщения
    phone_number: str
    message: str

@app.get("/send-message/")
async def api_send_message_get(phone_number: str, message: str):
    """
    Обработка GET-запроса на отправку сообщения.
    """
    try:
        # USER_DATA_DIR = "user_data"
        logger.info("Обработка GET-запроса на отправку сообщения. Номер: %s", phone_number)
        await check_user_data_dir(USER_DATA_DIR)

        # Проверка состояния браузера и отправка сообщения
        if not browser_manager.is_browser_running():
            logger.info("Браузер не запущен. Запуск...")
            await browser_manager.start_browser(USER_DATA_DIR)

        browser_manager.reset_timer()
        await send_message(browser_manager.browser_context, phone_number, message)
        logger.info("Сообщение успешно отправлено: Номер: %s", phone_number)
        return {"status": "success", "message": "Сообщение успешно отправлено!"}
    except Exception as e:
        logger.error("Ошибка в API (GET): %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # # Запуск сервера Prometheus для метрик
    # start_http_server(8001)

    # Запуск приложения
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
