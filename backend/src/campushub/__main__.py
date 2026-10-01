from fastapi import FastAPI
from .api.health import health_router

app = FastAPI(root_path="/api")

app.include_router(health_router)

