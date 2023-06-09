# dash-apps

Dashboard Apps Repo

This is a monorepo containing multiple Dash applications which can be deployed separately

The repo will eventually also contain a component library and standard assets and resources
to be shared across all Klima Dash apps.

## Local Development with Docker

### Prepare environnement

Create an .env file that contains at least the following variables:

```
WEB3_INFURA_PROJECT_ID
PREFECT_API_KEY
PREFECT_API_URL
```

You can control the behaviour of the environment by setting additionnal variables:

```
DASH_MAX_RECORDS
DASH_PRICE_DAYS
DASH_USE_LOCAL_STORAGE
```

### Launch environment

To set up a local development environment with `docker-compose` run:

```bash
docker-compose up
```

This will start a local
