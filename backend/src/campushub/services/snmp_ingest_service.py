from campushub.models.classification_result import ClassificationResult
from campushub.models.snmp_device_snapshot import SnmpDeviceSnapshot
from ..repositories.snmp_system_repository import SnmpSystemRepository
from ..repositories.snmp_interface_repository import SnmpInterfaceRepository
from ..repositories.snmp_ip_address_repository import SnmpIpAddressRepository
from ..repositories.snmp_route_repository import SnmpRouteRepository
from campushub.services.event_service import EventService


class SnmpIngestService:
    def __init__(self) -> None:
        self.system_repository = SnmpSystemRepository()
        self.interface_repository = SnmpInterfaceRepository()
        self.ip_address_repository = SnmpIpAddressRepository()
        self.route_repository = SnmpRouteRepository()
        self.event_service = EventService()

    def process_snapshot(
        self, snapshot: SnmpDeviceSnapshot, *, detect_events: bool = True
    ) -> ClassificationResult | None:
        device_id = snapshot.system.device_id
        result = self.event_service.detect_events(snapshot) if detect_events else None

        self.system_repository.upsert(snapshot.system)
        self.interface_repository.replace_for_device(device_id, snapshot.interfaces)
        self.ip_address_repository.replace_for_device(device_id, snapshot.ip_addresses)
        self.route_repository.replace_for_device(device_id, snapshot.routes)

        return result

