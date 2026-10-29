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
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(str, Enum): 
    INTERFACE_DOWN = "interface_down"
    INTERFACE_UP = "interface_up"
    INTERFACE_ADMIN_DOWN = "interface_admin_down"
    INTERFACE_ADMIN_UP = "interface_admin_up"
    IP_ADDRESS_REMOVED = "ip_address_removed"
    IP_ADDRESS_ADDED = "ip_address_added"
    ROUTE_REMOVED = "route_removed"
    ROUTE_ADDED = "route_added"

class ModifierType(str, Enum):
    ADMINISTRATIVE_SHUTDOWN = "administrative_shutdown"
    ROUTE_REMOVED_INTERFACE_DOWN = "route_removed_interface_down"
    DEFAULT_ROUTE_REMOVED = "default_route_removed"

class EventSource(str, Enum):
    SNMP_POLL = "snmp_poll"
    SNMP_TRAP = "snmp_trap"
    SYSLOG = "syslog"
    SYSTEM = "system"


