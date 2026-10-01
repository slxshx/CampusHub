from pydantic import BaseModel, IPvAnyAddress


class RouteDetail(BaseModel):
    interface_index: int
    destination: IPvAnyAddress
    subnet_mask: IPvAnyAddress | None = None
    next_hop: IPvAnyAddress | None = None
    route_type: int | None = None
    protocol: int | None = None
    age: int | None = None
