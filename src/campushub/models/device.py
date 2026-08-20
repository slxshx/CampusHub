from pydantic import BaseModel

class Device(BaseModel):
    host_name: str
    host_ip: str
    cpu: float
    ram: float
    interfaces: list[str]
    uptime: int
