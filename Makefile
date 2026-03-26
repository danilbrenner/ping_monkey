VENV        := .venv
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
MYPY        := $(VENV)/bin/mypy
PYTEST      := $(VENV)/bin/pytest
IMAGE_NAME  := ping_monkey

.DEFAULT_GOAL := help

.PHONY: help init install type-check t test docker-build

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

init: $(VENV)/bin/activate ## Create virtual environment
	@echo "Virtual environment ready at $(VENV)/"

install: init ## Install all dependencies (runtime + dev)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -r requirements-dev.txt
	@echo "Dependencies installed."

type-check: ## Run mypy static type checker
	$(MYPY) src

tc: type-check ## Alias for type-check

test: ## Run pytest
	$(PYTEST)

docker-build: ## Build the Docker image
	docker build -t $(IMAGE_NAME) .
