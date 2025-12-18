#!/bin/bash
set -e

echo "Ожидание готовности PostgreSQL..."
# Простая проверка доступности порта
until nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432} 2>/dev/null; do
  echo "PostgreSQL недоступен - ожидание..."
  sleep 2
done

echo "PostgreSQL готов!"

echo "Применение миграций..."
uv run alembic upgrade head || echo "Предупреждение: ошибка при применении миграций"

echo "Запуск бота..."
exec "$@"

