from ..repositories.snmp_system_repository import SnmpSystemRepository
from ..repositories.snmp_interface_repository import SnmpInterfaceRepository
from ..repositories.snmp_ip_address_repository import SnmpIpAddressRepository
from ..repositories.snmp_route_repository import SnmpRouteRepository
from ..repositories.managed_device_repository import ManagedDeviceRepository

from ..schemas.device_summary import DeviceSummary
from ..schemas.device_detail import DeviceDetail
from ..schemas.interface_detail import InterfaceDetail
from ..schemas.ip_address_detail import IpAddressDetail
from ..schemas.route_detail import RouteDetail
from ..schemas.system_detail import SystemDetail

class DeviceReadService():
    def __init__(self) -> None:
        self.managed_device: ManagedDeviceRepository = ManagedDeviceRepository()
        self.system: SnmpSystemRepository = SnmpSystemRepository()

    def get_devices(self):
        managed_devices = self.managed_device.get_devices()
        summaries = []

        for device in managed_devices:
            system = self.system.get_by_device(device.id)
            if system:
                summary = DeviceSummary()



        
    def get_device_detail(self, device_id):
