# CPU-only worker. No GPUs, social credentials, provider subscriptions or paid API calls.
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY clipfarm /app/clipfarm
COPY farmworker /app/farmworker
CMD ["python", "-m", "farmworker", "--root", "/farm", "work"]
