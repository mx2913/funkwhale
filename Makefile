SHELL := bash
CPU_CORES := $(shell N=$$(nproc); echo $$(( $$N > 4 ? 4 : $$N )))

BAKE_FILES = \
	docker-bake.json \
	docker-bake.api.json \
	docker-bake.front.json

docker-bake.%.json:
	./scripts/build_metadata.py --format bake --bake-target $* --bake-image docker.io/funkwhale/$* > $@

docker-metadata: $(BAKE_FILES)

docker-build: docker-metadata
	docker buildx bake $(foreach FILE,$(BAKE_FILES), --file $(FILE)) --print $(BUILD_ARGS)
	docker buildx bake $(foreach FILE,$(BAKE_FILES), --file $(FILE)) 		 $(BUILD_ARGS)

build-metadata:
	./scripts/build_metadata.py --format env | tee build_metadata.env

VERSION ?= $(shell git describe --tags --abbrev=0)
BUILD_DIR = dist
build:
	rm -Rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	tar --create --gunzip --file='$(BUILD_DIR)/funkwhale-api-$(VERSION).tar.gz' \
		--owner='root' \
		--group='root' \
		--exclude-vcs \
		api/config \
		api/funkwhale_api \
		api/install_os_dependencies.sh \
		api/manage.py \
		api/poetry.lock \
		api/pyproject.toml \
		api/Readme.md

	cd '$(BUILD_DIR)' && \
	tar --extract --gunzip --file='funkwhale-api-$(VERSION).tar.gz' && \
	zip -q 'funkwhale-api-$(VERSION).zip' -r api && \
	rm -Rf api

	tar --create --gunzip --file='$(BUILD_DIR)/funkwhale-front-$(VERSION).tar.gz' \
		--owner='root' \
		--group='root' \
		--exclude-vcs \
		--transform='s/^front\/dist/front/' \
		front/dist

	cd '$(BUILD_DIR)' && \
	tar --extract --gunzip --file='funkwhale-front-$(VERSION).tar.gz' && \
	zip -q 'funkwhale-front-$(VERSION).zip' -r front && \
	rm -Rf front

	cd '$(BUILD_DIR)' && sha256sum * > SHA256SUMS
