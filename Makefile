DOCKER_USER=klimadao
DOCKER_IMAGE=dash-apps
DOCKER_TAG=$(shell git rev-parse HEAD)
DOCKER_IMAGE_DEPLOY=dash-apps-deploy
DOCKER_TARGET_BASE=--target base
DOCKER_TARGET_PROD=--target prod
DOCKER_TARGET_DEPLOY=--target deploy
DOCKER_DEPLOY_ENV=-e DIGITALOCEAN_ACCESS_TOKEN=$(DIGITALOCEAN_ACCESS_TOKEN)
VOLUMES=-v $(shell pwd)/src:/opt/src

replace_variables:
	@echo "Replacing secrets in app-spec.yml"
	/usr/local/bin/envsubst -no-unset -no-empty -i app-spec.yml -o app-spec-new.yml && mv app-spec-new.yml app-spec.yml

install_envsubst:
	@echo "Installing envsubst"
	wget -O /usr/local/bin/envsubst https://github.com/a8m/envsubst/releases/download/v1.2.0/envsubst-`uname -s`-`uname -m`
	chmod +x /usr/local/bin/envsubst

build:
	docker build $(DOCKER_TARGET_BASE) -t $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG) .

build_deploy:
	docker build $(DOCKER_TARGET_DEPLOY) -t $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) .

shell: build_deploy
	@[ "${DIGITALOCEAN_ACCESS_TOKEN}" ] || ( echo "DIGITALOCEAN_ACCESS_TOKEN must be set in order to deploy"; exit 1 )
	docker run -it --rm $(DOCKER_DEPLOY_ENV) $(VOLUMES) $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) /bin/bash

deploy: build_deploy
	@echo "*** Deploying app"
	@[ "${DIGITALOCEAN_ACCESS_TOKEN}" ] || ( echo "DIGITALOCEAN_ACCESS_TOKEN must be set in order to deploy"; exit 1 )
	@[ "${DIGITALOCEAN_APP_ID}" ] || ( echo "DIGITALOCEAN_APP_ID must be set in order to deploy"; exit 1 )
	docker run -it --rm $(DOCKER_DEPLOY_ENV) $(VOLUMES) $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) bash -c 'doctl apps update $(DIGITALOCEAN_APP_ID) --spec app-spec.yml --wait --verbose'

create: build_deploy
	@echo "*** Creating app"
	@[ "${DIGITALOCEAN_ACCESS_TOKEN}" ] || ( echo "DIGITALOCEAN_ACCESS_TOKEN must be set in order to deploy"; exit 1 )
	docker run -it --rm $(DOCKER_DEPLOY_ENV) $(VOLUMES) $(DOCKER_USER)/$(DOCKER_IMAGE_DEPLOY):$(DOCKER_TAG) bash -c 'doctl apps create --spec app-spec.yml --wait --verbose'
