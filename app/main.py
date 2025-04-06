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
    
    
@app.post("/send-message/")
async def send_message_api(data: MessageRequest):
    logger.info(f"Запрос на /send-message:\nканал: {data.channel};\nномер: {data.phone_number};\nсообщение: {data.message}")

    try:
        await browser_manager.ensure_browser(USER_DATA_DIR)
        browser_manager.reset_timer()

        # подготовим ответы
        responses = []

        # отправка в WhatsApp
        if data.channel in ("whatsapp", "both"):
            try:
                logger.info("Отправка в WhatsApp.")
                await send_message_whatsapp(browser_manager.browser_context, data.phone_number, data.message)
                responses.append("Сообщение успешно отправлено через WhatsApp.")
            except Exception as e:
                logger.error(f"Ошибка при отправке через WhatsApp: {e}")
                responses.append(f"Ошибка при отправке через WhatsApp: {str(e)}")

        # отправка в Telegram
        if data.channel in ("telegram", "both"):
            try:
                logger.info("Отправка в Telegram.")
                await send_message_telegram(browser_manager.browser_context, data.phone_number, data.message)
                responses.append("Сообщение успешно отправлено через Telegram")
            except Exception as e:
                logger.error(f"Ошибка при отправке через Telegram: {e}")
                responses.append(f"Ошибка при отправке через Telegram: {str(e)}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "\n".join(responses)
            }
        )

    except Exception as e:
        logger.error(f"Глобальная ошибка: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Ошибка при обработке запроса",
                "error": str(e)
            }
        )