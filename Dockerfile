FROM python:3.13-slim

# Niente file .pyc e log subito visibili con `docker compose logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ bot/

# Il bot non ha bisogno dei privilegi di root
RUN useradd --create-home --uid 1000 bot
USER bot

CMD ["python", "-m", "bot.main"]
