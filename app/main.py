from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.browser_manager import browser_manager, check_user_data_dir
from app.whatsapp import send_message
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

USER_DATA_DIR = "user_data"

@app.on_event("startup")
async def startup_event():
    await check_user_data_dir(USER_DATA_DIR)

@app.get("/send-message/")
async def api_send_message_get(phone_number: str, message: str):
    try:
        logger.info("Запрос отправки сообщения: %s", phone_number)
        if not browser_manager.is_browser_running():
            await browser_manager.start_browser(USER_DATA_DIR)

        browser_manager.reset_timer()
        await send_message(browser_manager.browser_context, phone_number, message)
        return {"status": "success", "message": "Сообщение успешно отправлено!"}
    except Exception as e:
        logger.error("Ошибка при отправке сообщения: %s", e)
        raise HTTPException(status_code=500, detail=str(e))