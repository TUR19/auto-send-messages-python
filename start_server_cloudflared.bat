:: Запуск FastAPI в новом окне
start cmd /k "call venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Ждём 10 секунд, чтобы сервер успел стартовать
timeout /t 10 /nobreak > nul

:: Запуск Cloudflare туннеля
start cmd /k "cloudflared tunnel run my-backend"
