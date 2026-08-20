from fastapi import APIRouter

device_router = APIRouter()

@device_router.get("/device", tags=["device"])
async def get_devices():
    return [
            {
                "host_name": "router_01",
                "host_ip": "192.168.178.10",
                "cpu": "31%",
                "ram": "67%",
                "interface_status": "Online",
                "uptime": "7h 13m 54s",
            },
            {
                "host_name": "router_02",
                "host_ip": "192.168.178.20",
                "cpu": "12%",
                "ram": "16%",
                "interface_status": "Online",
                "uptime": "3h 26m 12s",
            }
        ]
