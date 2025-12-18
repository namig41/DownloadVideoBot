FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install --no-cache-dir uv

# Рабочая директория
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml ./
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Копирование README.md если существует (опционально, для pyproject.toml)
COPY README.md* ./

# Копирование uv.lock если существует (опционально)
COPY uv.lock* ./

# Установка зависимостей через uv
# Используем --frozen только если uv.lock существует
RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

# Создание директорий для данных и загрузок
RUN mkdir -p data downloads

# Копирование entrypoint скрипта
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Точка входа
CMD ["uv", "run", "python", "src/bot/main.py"]

