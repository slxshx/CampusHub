from campushub.models.snmp_device_snapshot import SnmpDeviceSnapshot
from ..repositories.snmp_system_repository import SnmpSystemRepository
from ..repositories.snmp_interface_repository import SnmpInterfaceRepository
from ..repositories.snmp_ip_address_repository import SnmpIpAddressRepository
from ..repositories.snmp_route_repository import SnmpRouteRepository
from campushub.services.event_service import EventService

class SnmpIngestService():
    def __init__(self) -> None:
        self.system_repository: SnmpSystemRepository = SnmpSystemRepository()
        self.interface_repository: SnmpInterfaceRepository = SnmpInterfaceRepository()
        self.ip_address_repository: SnmpIpAddressRepository = SnmpIpAddressRepository()
        self.route_repository: SnmpRouteRepository = SnmpRouteRepository()
        self.event_service: EventService = EventService()

    def process_snapshot(self, snapshot: SnmpDeviceSnapshot) -> None:
        device_id = snapshot.system.device_id
        self.event_service.detect_events(snapshot)
        _ = self.system_repository.upsert(snapshot.system)
        self.interface_repository.replace_for_device(device_id, snapshot.interfaces)
        self.ip_address_repository.replace_for_device(device_id, snapshot.ip_addresses)
        self.route_repository.replace_for_device(device_id, snapshot.routes)

