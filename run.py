import uvicorn
from dotenv import load_dotenv
import os

# Пытаемся загрузить переменные окружения из различных файлов
load_dotenv('.env.development')
load_dotenv('.env')

# Устанавливаем переменные окружения если они не заданы
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:1234@localhost:5432/schedule_db'
if not os.getenv('POSTGRES_USER'):
    os.environ['POSTGRES_USER'] = 'postgres'
if not os.getenv('POSTGRES_PASSWORD'):
    os.environ['POSTGRES_PASSWORD'] = '1234'
if not os.getenv('POSTGRES_DB'):
    os.environ['POSTGRES_DB'] = 'schedule_db'

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
