from pydantic import BaseModel

from .ip_address_detail import IpAddressDetail


class InterfaceDetail(BaseModel):
    if_index: int
    description: str | None = None
    interface_type: int | None = None
    mtu: int | None = None
    speed: int | None = None
    mac_address: str | None = None
    admin_status: int | None = None
    oper_status: int | None = None
    ip_addresses: list[IpAddressDetail]
