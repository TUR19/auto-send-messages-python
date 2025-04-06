from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.browser_manager import browser_manager, check_user_data_dir
from app.whatsapp import send_message_whatsapp
from app.telegram import send_message_telegram
from app.models import MessageRequest
import logging
import os

# Создаем папку logs, если не существует
os.makedirs("logs", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()  # Также выводим в консоль
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware добавлен.")

USER_DATA_DIR = "user_data"

@app.on_event("startup")
async def startup_event():
    logger.info("Событие запуска приложения. Проверка user_data_dir...")
    await check_user_data_dir(USER_DATA_DIR)
    logger.info("Startup завершён успешно.")

# POST для WhatsApp
@app.post("/send-message-whatsapp/")
async def api_send_message_post(data: MessageRequest):
    logger.info(f"Получен POST-запрос: /send-message-whatsapp -> номер: {data.phone_number}, сообщение: {data.message}")
    try:
        await browser_manager.ensure_browser(USER_DATA_DIR)
        browser_manager.reset_timer()
        logger.info("Отправка сообщения в WhatsApp начинается...")
        await send_message_whatsapp(browser_manager.browser_context, data.phone_number.replace(" ", ""), data.message)
        logger.info("Сообщение успешно отправлено через WhatsApp.")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Сообщение успешно отправлено через WhatsApp.",
                "error": None
            }
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке WhatsApp-сообщения: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Ошибка при отправке WhatsApp-сообщения",
                "error": str(e)
            }
        )

# POST для Telegram
@app.post("/send-message-telegram/")
async def api_send_message_post(data: MessageRequest):
    logger.info(f"Получен POST-запрос: /send-message-telegram -> номер: {data.phone_number}, сообщение: {data.message}")
    try:
        await browser_manager.ensure_browser(USER_DATA_DIR)
        browser_manager.reset_timer()
        logger.info("Отправка сообщения в Telegram начинается...")
        await send_message_telegram(browser_manager.browser_context, data.phone_number.replace(" ", ""), data.message)
        logger.info("Сообщение успешно отправлено через Telegram.")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Сообщение успешно отправлено через Telegram.",
                "error": None
            }
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке Telegram-сообщения: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Ошибка при отправке Telegram-сообщения",
                "error": str(e)
            }
        )