# FastAPI Server Time API

Простой тестовый бэкэнд на FastAPI, возвращающий текущее время сервера.

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
- `GET /time/moscow` - текущее время в часовом поясе `Europe/Moscow`

Документация FastAPI доступна на `/docs`.
