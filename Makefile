EX = docker exec -it
PYTEST = ${EX} app pytest
DC = docker compose
BUILD = docker build -t devcontainer -f .devcontainer/Dockerfile .

.PHONY: build
build:
	${BUILD}

.PHONY: up
up:
	${DC} -f .devcontainer/compose.yaml up --build

.PHONY: bash
bash:
	${EX} app bash

.PHONY: tests
tests:
	${PYTEST} tests/

.PHONY: sync-tests
sync-tests:
	${PYTEST} tests/sync_tests

.PHONY: async-tests
async-tests:
	${PYTEST} tests/async_tests

.PHONY: test-utils
test-utils:
	pytest tests/test_utils
