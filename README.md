# Take home assignment for backend position

Threat Intelligence API Development

## How to run

### Locally:

1. Create a virtualenv and install deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the API

```bash
uvicorn app.main:app --reload
```

3. Run tests

```bash
pytest
```

## Locally in Docker

```bash
docker build -t threat-api .
docker run -p 8000:8000 threat-api
```

## Connect to local

http://localhost:8000/api/indicators

## Swagger Documentation

http://localhost:8000/docs

## Use the live api
