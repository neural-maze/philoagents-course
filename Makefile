ifeq (,$(wildcard philoagents-api/.env))
$(error .env file is missing in philoagents-api/. Please create one based on .env.example)
endif

include philoagents-api/.env

# --- Infrastructure ---

infrastructure-build:
	docker compose build

infrastructure-up:
	docker compose up --build -d

infrastructure-stop:
	docker compose stop

check-docker-image:
	@if [ -z "$$(docker images -q philoagents-api 2> /dev/null)" ]; then \
		echo "Error: philoagents-api Docker image not found."; \
		echo "Please run 'make infrastructure-build' first to build the required images."; \
		exit 1; \
	fi

# --- Offline Pipelines ---

create-long-term-memory: check-docker-image
	docker run --rm --network=philoagents-network --env-file philoagents-api/.env -v ./data:/app/data philoagents-api uv run python -m tools.create_long_term_memory

delete-long-term-memory: check-docker-image
	docker run --rm --network=philoagents-network --env-file philoagents-api/.env philoagents-api uv run python -m tools.delete_long_term_memory

generate-evaluation-dataset: check-docker-image
	docker run --rm --network=philoagents-network --env-file philoagents-api/.env -v ./data:/app/data philoagents-api uv run python -m tools.generate_evaluation_dataset --max-samples 15

evaluate-agent: check-docker-image
	docker run --rm --network=philoagents-network --env-file philoagents-api/.env -v ./data:/app/data philoagents-api uv run python -m tools.evaluate_agent --workers 1 --nb-samples 15

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
