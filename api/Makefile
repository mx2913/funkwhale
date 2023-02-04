SHELL := bash
CPU_CORES := $(shell N=$$(nproc); echo $$(( $$N > 4 ? 4 : $$N )))

.PHONY: install lint

install:
	poetry install --all-extras

export DJANGO_SETTINGS_MODULE=config.settings.local

lint:
	poetry run pylint \
		--jobs=$(CPU_CORES) \
		--output-format=colorized \
		--recursive=true \
		config funkwhale_api tests

SCHEMA_FILE ?= schema.yml
schema:
	poetry run funkwhale-manage spectacular --file $(SCHEMA_FILE)
	if command -v npx > /dev/null; then npx prettier --write $(SCHEMA_FILE); fi
