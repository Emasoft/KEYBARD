run := uv run

.PHONY: test
test:
	$(run) pytest tests/ -n 16 --dist=loadgroup $(ARGS)

.PHONY: testv
testv:
	$(run) pytest tests/ -vvv -n 16 --dist=loadgroup $(ARGS)

.PHONY: test-snapshot-update
test-snapshot-update:
	$(run) pytest tests/ --snapshot-update -n 16 --dist=loadgroup $(ARGS)

.PHONY: test-coverage
test-coverage:
	$(run) pytest tests/ --cov-report term-missing --cov=keybard -n 16 --dist=loadgroup $(ARGS)

.PHONY: coverage
coverage:
	$(run) coverage html

.PHONY: typecheck
typecheck:
	$(run) mypy src/keybard

.PHONY: format
format:
	$(run) ruff format --line-length=320 src tests

.PHONY: format-check
format-check:
	$(run) ruff format --check --line-length=320 src tests

.PHONY: faq
faq:
	$(run) faqtory build

.PHONY: setup
setup:
	uv install
	uv install --extras syntax

.PHONY: update
update:
	uv self update

.PHONY: install-pre-commit
install-pre-commit:
	$(run) pre-commit install

.PHONY: repl
repl:
	$(run) python
