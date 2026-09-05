from fastapi import APIRouter
from ..models.device import Device

device_router = APIRouter()

@device_router.get("/device", response_model=list[Device])
async def get_devices():
    return [
            {
                "host_name": "router_01",
                "host_ip": "192.168.178.10",
                "cpu": 31.2,
                "ram": 88.2,
                "interfaces": ["g0/0", "g0/1"],
                "uptime": 2321,
            },
                        {
                "host_name": "router_02",
                "host_ip": "192.168.178.20",
                "cpu": 11.8,
                "ram": 88.2,
                "interfaces": ["g0/0", "g0/1"],
                "uptime": 1002,
            },
        ]
