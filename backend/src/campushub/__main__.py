from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from campushub.api.device import device_router
from campushub.api.health import health_router
from campushub.api.event import event_router

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(device_router)
app.include_router(event_router)
