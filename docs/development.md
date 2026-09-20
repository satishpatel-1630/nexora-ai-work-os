# Development

## API
`\.\.venv\\Scripts\\python.exe -m pip install -e ".[dev]"`
`\.\.venv\\Scripts\\python.exe -m uvicorn apps.api.app.main:app --reload`

## Web
`cd apps/web`
`npm.cmd install`
`npm.cmd run dev`

## Database
`alembic upgrade head`

## Tests
`\.\.venv\\Scripts\\python.exe -m pytest`

PowerShell execution policy should not be weakened. Use direct executables such as `\.\.venv\\Scripts\\python.exe` and `npm.cmd`.
