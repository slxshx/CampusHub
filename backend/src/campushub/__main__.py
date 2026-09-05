from fastapi import FastAPI
from .api.health import health_router
from .api.device import device_router

app = FastAPI(root_path="/api")

app.include_router(health_router)
app.include_router(device_router)

