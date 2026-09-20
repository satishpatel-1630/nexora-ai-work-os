from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NEXORA API", version="0.1.0")

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="nexora-api", version="0.1.0")

@app.get("/api/v1")
async def api_root() -> dict[str, str]:
    return {"name": "NEXORA", "status": "foundation"}
