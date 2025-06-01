# Justfile for Messaging API Backend Assignment

# Development commands
install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload

# Database commands
migrate:
	alembic upgrade head

# Docker commands
up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up --build -d

# Testing commands
test:
	pytest

# Code formatting
format:
	black .
	isort .

# Optional: MCP server
mcp:
	python -m app.mcp_server

# Create new migration
create-migration message:
	alembic revision --autogenerate -m "{{message}}"

# Initialize database
init-db:
	alembic init alembic
	alembic revision --autogenerate -m "Initial migration"
	alembic upgrade head
