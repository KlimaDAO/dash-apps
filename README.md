# dash-apps
Dashboard Apps Repo

This is a monorepo containing multiple Dash applications which can be deployed separately

The repo will eventually also contain a component library and standard assets and resources
to be shared across all Klima Dash apps.

## Local Development

To build a local development environment, first use Docker to run a Python
container:

```bash
docker run -v $PWD:/usr/local/src -it -p 8050:8050 -w /usr/local/src python:3.10 bash
```

Since this command mounts your local working directory into the container,
any changes made to the code will immediately be reflected inside the container.
Therefore, the Dash dev server's hot-reload functionality should work normally.

Next, install the requirements inside that container:

```bash
pip install -r requirements.txt
```

Now simply run whichever app you want:

```bash
python -m src.apps.yield_offset.app
```
