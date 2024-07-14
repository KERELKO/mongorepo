EX = docker exec -it
PYTEST = ${EX} app pytest


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

.PHONY: test-notimpl
test-notimpl:
	${PYTEST} tests/sync_tests/test_not_implemented.py

.PHONY: test-utils
test-utils:
	${PYTEST} tests/test_utils
