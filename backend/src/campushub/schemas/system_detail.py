from pydantic import BaseModel


class SystemDetail(BaseModel):
    description: str | None = None
    object_id: str | None = None
    uptime: int | None = None
    name: str | None = None
    location: str | None = None
