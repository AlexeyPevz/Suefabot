.PHONY: help build up down logs clean test init-db

# Default target
help:
	@echo "Suefabot Development Commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make init-db     - Initialize database with starter data"
	@echo "  make dev         - Start development environment"
	@echo "  make prod        - Start production environment"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start development environment
dev:
	docker-compose up -d postgres redis
	@echo "Starting backend..."
	cd backend && python app.py &
	@echo "Starting bot..."
	cd bot && python main.py &
	@echo "Starting webapp..."
	cd webapp && npm start &
	@echo "Development environment started!"

# Start production environment
prod:
	docker-compose --profile production up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# View specific service logs
logs-%:
	docker-compose logs -f $*

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Run tests
test:
	cd backend && python -m pytest
	cd webapp && npm test

# Initialize database
init-db:
	docker-compose run --rm backend python init_database.py

# Connect to database
db-shell:
	docker-compose exec postgres psql -U suefabot -d suefabot

# Connect to Redis
redis-cli:
	docker-compose exec redis redis-cli

# Check service health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:5000/health || echo "Backend is down"
	@curl -s http://localhost:3000 || echo "Webapp is down"

# Development shortcuts
backend:
	cd backend && python app.py

bot:
	cd bot && python main.py

webapp:
	cd webapp && npm start

worker:
	cd backend && python timeout_worker.py