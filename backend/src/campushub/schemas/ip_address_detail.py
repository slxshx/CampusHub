from pydantic import BaseModel, IPvAnyAddress


class IpAddressDetail(BaseModel):
    address: IPvAnyAddress
    subnet_mask: IPvAnyAddress | None = None
