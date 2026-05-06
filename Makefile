.PHONY: up down test logs clean build help

up:              ## Start all services
	docker compose up --build -d
	@echo ""
	@echo "🟢 frontend:  http://localhost:3000"
	@echo "🟢 API Docs:  http://localhost:8000/docs"
	@echo "🟢 Health:    http://localhost:8000/api/v1/health"

down:            ## Stop all services and remove volumes
	docker compose down -v

build:           ## Build without starting
	docker compose build

test:            ## Run backend tests
	docker compose exec backend pytest -v

logs:            ## Tail all service logs
	docker compose logs -f --tail=50

logs-backend:    ## Tail backend logs only
	docker compose logs -f --tail=50 backend

health:          ## Check service health
	@curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

clean:           ## Remove all containers, volumes, and build artifacts
	docker compose down -v --rmi local
	rm -rf frontend/dist backend/__pycache__

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
