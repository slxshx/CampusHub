from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel

class Metric(BaseModel):
    TABLE_NAME: ClassVar[str] = "metrics"

    id: int
    device_id: int
    timestamp: datetime
    cpu_usage: float | None = None
    ram_usage: float | None = None
    storage_usage: float | None = None
    temperature: float | None = None
    uptime: int | None = None

class CreateMetric(BaseModel):
    TABLE_NAME: ClassVar[str] = "metrics"

    device_id: int
    timestamp: datetime
    cpu_usage: float | None = None
    ram_usage: float | None = None
    storage_usage: float | None = None
    temperature: float | None = None
    uptime: int | None = None

class UpdateMetric(BaseModel):
    TABLE_NAME: ClassVar[str] = "metrics"

    cpu_usage: float | None = None
    ram_usage: float | None = None
    storage_usage: float | None = None
    temperature: float | None = None
    uptime: int | None = None


