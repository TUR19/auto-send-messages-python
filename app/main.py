from fastapi import FastAPI, HTTPException
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

@app.get("/send-message-whatsapp/")
async def api_send_message_get(phone_number: str, message: str):
    logger.info(f"Получен GET-запрос: /send-message-whatsapp?phone_number={phone_number}&message={message}")
    try:
        await browser_manager.ensure_browser(USER_DATA_DIR)
        browser_manager.reset_timer()
        logger.info("Отправка сообщения начинается...")
        await send_message_whatsapp(browser_manager.browser_context, phone_number.replace(" ", ""), message)
        logger.info("Сообщение успешно отправлено.")
        return {"status": "success", "message": "Сообщение успешно отправлено!"}
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/send-message-telegram/")
async def api_send_message_get(phone_number: str, message: str):
    logger.info(f"Получен GET-запрос: /send-message-telegram?phone_number={phone_number}&message={message}")
    try:
        await browser_manager.ensure_browser(USER_DATA_DIR)
        browser_manager.reset_timer()
        logger.info("Отправка сообщения начинается...")
        await send_message_telegram(browser_manager.browser_context, phone_number.replace(" ", ""), message)
        logger.info("Сообщение успешно отправлено.")
        return {"status": "success", "message": "Сообщение успешно отправлено!"}
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))