FROM --platform=linux/amd64 python:3.8-slim AS base

# Set Python interpreter flags
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install dependencies and do cleanup to save space
RUN apt-get update && \
    apt-get install -y \
    make \
    gcc \
    && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

# *** We use this image to run the bots
FROM base AS prod

# We need to run the source code in the Docker image on Digital Ocean, so copy that in
# This is a public repo, so there is nothing proprietary that shouldn't be in the image
COPY src src

# *** We use this image for deployment
FROM base AS deploy

# We install go (and force the platform, above, because of that)
RUN apt-get update && \
    apt-get install -y \
    wget
ARG GO_FILE=go1.17.linux-amd64.tar.gz
RUN wget https://golang.org/dl/${GO_FILE} && \
    tar xvfz ${GO_FILE} && \
    mv go /usr/local/go && \
    rm ${GO_FILE}
ENV GOROOT=/usr/local/go
ENV GOPATH=/opt/goProjects
ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH
RUN mkdir -p $GOPATH

# Install doctl from source
# The latest version (1.68.0) does not return an error code if the deployment fails, so we use a specific git commit
# The GO111MODULE variable is from: https://newbedev.com/getting-gopath-error-go-cannot-use-path-version-syntax-in-gopath-mode-in-ubuntu-16-04
RUN GO111MODULE=on go install github.com/digitalocean/doctl/cmd/doctl@2fcbadcb46efd8dca0d93fbef2a3a8394f5981ba

COPY Makefile Makefile

# Install envsubst and move into place
RUN make install_envsubst

COPY app-spec.yml app-spec.yml

# Ensures that variables in app-spec.yml are replaced every time
ENTRYPOINT make replace_variables
