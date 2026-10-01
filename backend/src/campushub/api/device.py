from fastapi import APIRouter, HTTPException

from campushub.schemas.device_detail import DeviceDetail
from campushub.schemas.device_summary import DeviceSummary

from campushub.services.device_read_service import DeviceReadService

device_router = APIRouter()
read_service = DeviceReadService()

@device_router.get("/devices", response_model=list[DeviceSummary])
async def get_devices():
    return read_service.get_devices()


@device_router.get("/devices/{device_id}", response_model=DeviceDetail)
async def get_device_detail(device_id: int):
    device = read_service.get_device_detail(device_id)

    if device is None:
        raise HTTPException(
                status_code = 404,
                detail = "Device not found."
                )
    return device


