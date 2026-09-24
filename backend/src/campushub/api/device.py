from fastapi import APIRouter
from ..models.device import Device

device_router = APIRouter()

@device_router.get("/device", response_model=list[Device])
async def get_devices():
    return [
            { 
                "id": 1,
                "hostname": "Test-Server",
                "description": "Kannst du mich sehen?",
                "device_type": "Server",
                "location": "Campussi",
            },
            {
                "id": 2,
                "hostname": "Test-Switch",
                "description": "Kannst du mich sehen?",
                "device_type": "Switch",
                "location": "Campussi",
            },
        ]
