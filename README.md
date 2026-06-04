# healthz
Library for implementing sync and async health checks

## Setup Environment

```sh
uv sync --dev --group jupyter
source .venv/bin/activate
jupyter lab
```

## Build
```sh
uv build
twine upload dist/*
```
