compose_command ?= docker-compose
docker_compose_file_path ?= infrastructure/docker/docker-compose.dev.yml
app_service ?= ioet-catalog-backend
db_name ?= ioet_catalog_db
db_user ?= root
db_password ?= toor
db_port ?= 5432

.PHONY: help
help: ## Show this help (usage: make help)
	@echo "Usage: make [target]"
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			target = $$1; \
			sub(/:/, "", target); \
			printf "  \033[36m%-20s\033[0m %s\n", target, substr($$0, RSTART + 3, RLENGTH); \
		} \
	}' $(MAKEFILE_LIST)

.PHONY: build
build:	## Build project with docker-compose
	${compose_command} -f ${docker_compose_file_path} build

.PHONY: up
up:	## Run all services in Docker (recommended for development)
	${compose_command} -f ${docker_compose_file_path} up -d

.PHONY: clean
clean:	## Remove everything (containers, volumes, images) - WARNING: This will delete all data
	${compose_command} -f ${docker_compose_file_path} down --volumes --remove-orphans --rmi all

.PHONY: stop
stop:	## Stop containers without removing data
	${compose_command} -f ${docker_compose_file_path} stop

.PHONY: ensure_containers
ensure_containers: ## Ensure Docker containers exist
	@if ! docker ps -a | grep -q ${app_service}; then \
		echo "Containers not found. Running initial setup..."; \
		$(MAKE) up; \
	fi

.PHONY: start
start: ensure_containers ## Start Docker containers (creates them if they don't exist)
	@echo "Starting containers..."
	${compose_command} -f ${docker_compose_file_path} start
	@echo "Containers started! The API will be available at http://localhost:8000"
	@echo "View the API documentation at http://localhost:8000/docs"

.PHONY: logs
logs:	## Show logs of all services
	${compose_command} -f ${docker_compose_file_path} logs -f
	
.PHONY: dev_shell
dev_shell:	## Run a dev shell
	@${compose_command} -f ${docker_compose_file_path} exec ${app_service} bash

.PHONY: create_dev_env
create_dev_env: ## Create Python virtual environment and install dependencies
	python3.10 -m venv .venv && \
	. .venv/bin/activate && \
	pip install poetry && \
	poetry install

.PHONY: ensure_postgres
ensure_postgres: ## Ensure PostgreSQL is running (starts in Docker if not found locally)
	@if ! pg_isready -h localhost -p ${db_port} >/dev/null 2>&1; then \
		echo "Local PostgreSQL not found, starting in Docker..."; \
		docker run --name postgres-local -e POSTGRES_USER=${db_user} -e POSTGRES_PASSWORD=${db_password} -e POSTGRES_DB=${db_name} -p ${db_port}:5432 -d postgres:15; \
		echo "Waiting for PostgreSQL to start..."; \
		until pg_isready -h localhost -p ${db_port} >/dev/null 2>&1; do sleep 1; done; \
	fi

.PHONY: local
local: create_dev_env ensure_postgres ## Start application locally (automatically sets up database)
	@echo "Starting application locally..."
	. .venv/bin/activate && \
	export DATABASE_URL=postgresql://${db_user}:${db_password}@localhost:${db_port}/${db_name} && \
	poetry run uvicorn main:app --reload --port 8000

.PHONY: test
test: create_dev_env ensure_postgres ## Run tests (automatically sets up database)
	@echo "Running tests..."
	. .venv/bin/activate && \
	export DATABASE_URL=postgresql://${db_user}:${db_password}@localhost:${db_port}/${db_name} && \
	poetry run pytest api/tests/api/product_routes_test.py -v

.PHONY: lint
lint: ## Run linter
	flake8 .

.PHONY: debug
debug: ## Show debug information
	@echo "Database URL: postgresql://${db_user}:${db_password}@localhost:${db_port}/${db_name}"
	@if pg_isready -h localhost -p ${db_port} >/dev/null 2>&1; then \
		echo "PostgreSQL is running"; \
	else \
		echo "PostgreSQL is not running"; \
	fi

.PHONY: win_create_dev_env
win_create_dev_env:
			python -m venv .venv && \
			.venv\Scripts\activate.bat && \
			pip install poetry && \
			poetry install

.PHONY: win_start
win_start:  ## Starts the debug of the program in windows environment
	.venv\Scripts\activate.bat && \
	.env && \
	uvicorn main:app --reload
