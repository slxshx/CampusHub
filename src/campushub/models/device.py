from pydantic import BaseModel

class Device(BaseModel):
    id: int
    hostname: str
    description: str | None
    device_type: str
    location: str | None
