.PHONY: help format lint test clean run docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make format      - Format code with black and isort"
	@echo "  make lint        - Run linters (ruff, black check, isort check)"
	@echo "  make test        - Run tests with pytest"
	@echo "  make clean       - Clean cache files"
	@echo "  make run         - Run the application locally"
	@echo "  make docker-up   - Start docker containers"
	@echo "  make docker-down - Stop docker containers"
	@echo "  make install     - Install dependencies"
	@echo "  make install-dev - Install dev dependencies"
	@echo "  make pre-commit  - Install pre-commit hooks"

format:
	@echo "Formatting code with black..."
	black app/ load_data.py
	@echo "Organizing imports with isort..."
	isort app/ load_data.py
	@echo "Done!"

lint:
	@echo "Running ruff..."
	ruff check app/ load_data.py
	@echo "Checking formatting with black..."
	black --check app/ load_data.py
	@echo "Checking import order with isort..."
	isort --check-only app/ load_data.py
	@echo "All checks passed!"

test:
	@echo "Running tests..."
	DATABASE_URL="sqlite+aiosqlite:///./test.db" ./venv/bin/python -m pytest app/test/ -v

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -f test.db
	@echo "Done!"

run:
	@echo "Starting Vlab API..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up --build -d
	@echo "Containers started!"
	@echo "API available at http://localhost:8000"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Containers stopped!"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Done!"

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt -r requirements-dev.txt
	@echo "Done!"

pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Done! Pre-commit hooks will run automatically on git commit."

migrations-create:
	@echo "Creating new migration..."
	alembic revision --autogenerate -m "$(msg)"

migrations-upgrade:
	@echo "Running migrations..."
	alembic upgrade head

migrations-downgrade:
	@echo "Rolling back last migration..."
	alembic downgrade -1

