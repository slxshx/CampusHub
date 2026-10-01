from enum import Enum

class DeviceType(str, Enum): 
    ROUTER = "router"
    SWITCH = "switch"
    SERVER = "server"
    CLIENT = "client"


class SnmpVersion(str, Enum):
    V2C = "v2c"
    V3 = "v3"

class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EventSource(str, Enum):
    SNMP_POLL = "snmp_poll"
    SNMP_TRAP = "snmp_trap"
    SYSLOG = "syslog"
    SYSTEM = "system"


