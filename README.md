# FastAPI Server Time API

Простой тестовый бэкэнд на FastAPI, возвращающий текущее время сервера и конвертирующий время между часовыми поясами (включая русские названия городов).

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload
```

После запуска:

- `GET /` - проверка, что API работает
- `GET /time` - текущее локальное время сервера
- `GET /date` - текущая локальная дата сервера
- `GET /time/moscow` - текущее время в часовом поясе Москвы
- `GET /convert_time` - конвертация времени между часовыми поясами
  - Параметры: `time` (время), `from_tz` (исходный пояс, по умолчанию UTC), `to_tz` (целевой пояс)
  - Поддерживаются IANA названия и русские названия городов: `Москва`, `Екатеринбург`, `Красноярск` и др.
  - Пример: `/convert_time?time=14:00&from_tz=UTC&to_tz=Москва`

## Запуск через Docker

### Сборка образа

```bash
docker build -t fastapi-time-api .
```

### Запуск контейнера

```bash
docker run -d \
  --name fastapi-time-api \
  --restart unless-stopped \
  -p 8000:8000 \
  fastapi-time-api
```

### Проверка

```bash
curl http://localhost:8000/
```

### Остановка и удаление

```bash
docker stop fastapi-time-api && docker rm fastapi-time-api
```

## CI/CD

При каждом пуше в `main` GitHub Actions автоматически собирает новый Docker-образ, загружает его в GitHub Container Registry и деплоит на удаленный сервер по SSH.

Документация FastAPI доступна на `/docs`.
