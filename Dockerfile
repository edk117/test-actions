# Базовый образ с Python.
FROM python:3.12-slim

# Рабочая папка внутри контейнера.
WORKDIR /app

# Не создавать __pycache__ и *.pyc файлы.
ENV PYTHONDONTWRITEBYTECODE=1

# Сразу выводить логи в консоль Docker.
ENV PYTHONUNBUFFERED=1

# Сначала копируем зависимости для кэша Docker.
COPY requirements.txt .

# Устанавливаем зависимости проекта.
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения.
COPY main.py .

# Документируем порт приложения.
EXPOSE 8000

# Запускаем FastAPI через Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
