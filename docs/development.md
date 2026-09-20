# Development

## API

`python -m venv .venv`
`\.\.venv\\Scripts\\python.exe -m pip install -e ".[dev]"`
`\.\.venv\\Scripts\\python.exe -m uvicorn apps.api.app.main:app --reload`

API: http://127.0.0.1:8000

## Web

`cd apps/web`
`npm.cmd install`
`npm.cmd run dev`

Web: http://127.0.0.1:3000

## Tests

`\.\.venv\\Scripts\\python.exe -m pytest`
