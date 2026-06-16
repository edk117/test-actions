from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query


app = FastAPI(title="Server Time API")

RUSSIAN_TZ_MAP: dict[str, str] = {
    "калининград": "Europe/Kaliningrad",
    "москва": "Europe/Moscow",
    "самара": "Europe/Samara",
    "екатеринбург": "Asia/Yekaterinburg",
    "омск": "Asia/Omsk",
    "красноярск": "Asia/Krasnoyarsk",
    "иркутск": "Asia/Irkutsk",
    "якутск": "Asia/Yakutsk",
    "владивосток": "Asia/Vladivostok",
    "магадан": "Asia/Magadan",
    "камчатка": "Asia/Kamchatka",
    "киев": "Europe/Kyiv",
    "мinsk": "Europe/Minsk",
    "астана": "Asia/Almaty",
    "ташкент": "Asia/Tashkent",
    "баку": "Asia/Baku",
    "ереван": "Asia/Yerevan",
    "тбилиси": "Asia/Tbilisi",
}


def resolve_timezone(name: str) -> str:
    value = name.strip().lower()
    return RUSSIAN_TZ_MAP.get(value, name)


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


@app.get("/time/moscow")
def moscow_time() -> dict[str, str]:
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    return {
        "timezone": "Europe/Moscow",
        "iso": now.isoformat(),
        "unix": str(now.timestamp()),
    }


@app.get("/convert_time")
def convert_time(
    time: str = Query(..., description="Время в формате HH:MM, HH:MM:SS или YYYY-MM-DD HH:MM[:SS]"),
    from_tz: str = Query("UTC", description="Исходный часовой пояс: IANA название или русское название, например 'Москва'"),
    to_tz: str = Query(..., description="Целевой часовой пояс: IANA название или русское название, например 'Екатеринбург'"),
) -> dict:
    try:
        source_zone = ZoneInfo(resolve_timezone(from_tz))
        target_zone = ZoneInfo(resolve_timezone(to_tz))

        formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M:%S", "%H:%M")
        naive: datetime | None = None
        for fmt in formats:
            try:
                naive = datetime.strptime(time, fmt)
                break
            except ValueError:
                continue

        if naive is None:
            return {
                "error": "Неверный формат времени. Используйте HH:MM, HH:MM:SS или YYYY-MM-DD HH:MM[:SS]",
            }

        if naive.tzinfo is not None:
            localized = naive
        else:
            if len(naive.strftime("%Y-%m-%d")) == 10:
                localized = naive.replace(tzinfo=source_zone)
            else:
                today = datetime.now(source_zone).date()
                localized = datetime.combine(today, naive.time(), tzinfo=source_zone)

        converted = localized.astimezone(target_zone)

        return {
            "original": time,
            "from_tz": from_tz,
            "to_tz": to_tz,
            "result": converted.strftime("%Y-%m-%d %H:%M:%S"),
            "iso": converted.isoformat(),
            "unix": str(converted.timestamp()),
        }
    except Exception as e:
        return {"error": str(e)}
