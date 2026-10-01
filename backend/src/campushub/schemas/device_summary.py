from pydantic import BaseModel, IPvAnyAddress

from ..models.enums import DeviceType


class DeviceSummary(BaseModel):
    id: int
    name: str | None = None
    management_ip: IPvAnyAddress
    device_type: DeviceType
    location: str | None = None
    enabled: bool
