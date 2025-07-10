.PHONY: help setup dev test clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Initial project setup
	./infrastructure/scripts/setup.sh

dev:  ## Start development environment
	docker-compose up -d
	@echo "Infrastructure started. Services available at:"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis: localhost:6379" 
	@echo "  MinIO: http://localhost:9001"

test:  ## Run all tests
	cd services/resume-parser && poetry run pytest

clean:  ## Clean up development environment
	docker-compose down -v
	docker system prune -f

logs:  ## Show infrastructure logs
	docker-compose logs -f

status:  ## Show service status
	docker-compose ps
