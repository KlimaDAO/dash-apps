# dash-apps

Dashboard Apps Repo

This is a monorepo containing multiple Dash applications which can be deployed separately

The repo will eventually also contain a component library and standard assets and resources
to be shared across all Klima Dash apps.

## Local Development without Docker

To start the application run the following commands.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements1.txt
pip install -r requirements2.txt
python -m src.apps.api.app
```

## Local Development with Docker

### Prepare environment

Create a .env file. See .env.dist from instructions

### Launch environment

To set up a local development environment with `docker-compose` run:

```bash
docker-compose up
```
