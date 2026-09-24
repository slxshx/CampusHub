from enum import Enum

class DeviceType(str, Enum): 
    ROUTER = "router"
    SWTITCH = "switch"
    SERVER = "server"
    CLIENT = "client"


class SnmpVersion(str, Enum):
    V2C = "v2c"
    V3 = "v3"
