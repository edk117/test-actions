from datetime import datetime

from fastapi import FastAPI


app = FastAPI(title="Server Time API")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Server Time API is running"}


@app.get("/time")
def server_time() -> dict[str, str]:
    now = datetime.now().astimezone()

    return {
        "timezone": str(now.tzinfo),
        "iso": now.isoformat(),
        "unix": str(now.timestamp()),
    }


@app.get("/date")
def server_date() -> dict[str, str]:
    today = datetime.now().astimezone().date()

    return {
        "date": today.isoformat(),
    }
