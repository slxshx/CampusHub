from fastapi import FastAPI

from campushub.api.device import device_router
from campushub.api.health import health_router

app = FastAPI(root_path="/api")

app.include_router(health_router)
app.include_router(device_router)
