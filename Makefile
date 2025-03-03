ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example)
endif

include .env

# --- Default Values ---

CHECK_DIRS := .

# --- Infrastructure ---

infrastructure-up:
	docker compose up --build -d

infrastructure-stop:
	docker compose stop

check-docker-image:
	@if [ -z "$$(docker images -q philoagents-api 2> /dev/null)" ]; then \
		echo "Error: philoagents-api Docker image not found."; \
		echo "Please run 'make infrastructure-up' first to build the required images."; \
		exit 1; \
	fi

# OFFLINE PIPELINES

create-long-term-memory: check-docker-image
	docker run --rm --network=philoagents-network --env-file .env philoagents-api uv run python -m tools.create_long_term_memory

delete-long-term-memory: check-docker-image
	docker run --rm --network=philoagents-network --env-file .env philoagents-api uv run python -m tools.delete_long_term_memory

generate-evaluation-dataset: check-docker-image
	docker run --rm --network=philoagents-network --env-file .env philoagents-api uv run python -m tools.generate_evaluation_dataset

evaluate-agent: check-docker-image
	docker run --rm --network=philoagents-network --env-file .env philoagents-api uv run python -m tools.evaluate_agent --workers 1 --nb-samples 10

# --- QA ---

format-fix:
	uv run ruff format $(CHECK_DIRS)
	uv run ruff check --select I --fix 

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)
