.PHONY: install sync migrate upgrade downgrade bot dev docker-build docker-up docker-down docker-logs docker-shell help

help:
	@echo "Доступные команды:"
	@echo "  make install     - Установить зависимости через uv"
	@echo "  make sync        - Синхронизировать зависимости (uv sync)"
	@echo "  make migrate     - Создать новую миграцию"
	@echo "  make upgrade     - Применить миграции"
	@echo "  make downgrade    - Откатить последнюю миграцию"
	@echo "  make bot         - Запустить бота"
	@echo "  make dev         - Запустить бота в режиме разработки"
	@echo ""
	@echo "Docker команды:"
	@echo "  make docker-build - Собрать Docker образ"
	@echo "  make docker-up    - Запустить контейнеры"
	@echo "  make docker-down  - Остановить контейнеры"
	@echo "  make docker-logs  - Показать логи контейнеров"
	@echo "  make docker-shell - Открыть shell в контейнере бота"

install:
	uv sync

sync:
	uv sync

migrate:
	uv run alembic revision --autogenerate -m "$(msg)"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

bot:
	uv run python src/bot/main.py

dev:
	uv run python src/bot/main.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

docker-shell:
	docker-compose exec bot /bin/bash

docker-pull:
	docker pull ghcr.io/$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/download_video:latest

docker-prod-up:
	docker-compose -f docker-compose.prod.yml up -d

docker-prod-down:
	docker-compose -f docker-compose.prod.yml down

