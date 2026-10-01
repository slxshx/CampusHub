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
        self.interface: SnmpInterfaceRepository = SnmpInterfaceRepository()
        self.ip_address: SnmpIpAddressRepository = SnmpIpAddressRepository()
        self.route: SnmpRouteRepository = SnmpRouteRepository()

    def get_devices(self) -> list[DeviceSummary]:
        managed_devices = self.managed_device.get_devices()
        summaries: list[DeviceSummary] = []

        for device in managed_devices:
            system = self.system.get_by_device(device.id)
            device_name = None
            device_location = None

            if system:
                device_name = system.name
                device_location = system.location

            summary = DeviceSummary(
                        id = device.id,
                        name = device_name,
                        management_ip = device.management_ip,
                        device_type = device.device_type,
                        location = device_location,
                        enabled = device.enabled
                        )

            summaries.append(summary)

        return summaries

        
    def get_device_detail(self, device_id: int) -> DeviceDetail|None:
        device = self.managed_device.get_device_by_id(device_id)
        if device is None:
            return None

        system_detail = None

        system = self.system.get_by_device(device_id)

        if system is not None:
            system_detail = SystemDetail(
                    description = system.description,
                    object_id = system.object_id,
                    uptime = system.uptime,
                    name = system.name,
                    location = system.location
                    )

 
        device_interfaces = self.interface.get_by_device(device_id)
        device_ip_addresses = self.ip_address.get_by_device(device_id)
        interface_details: list[InterfaceDetail] = []

        for interface in device_interfaces:
            ip_addresses: list[IpAddressDetail] = []
            for device_ip_address in device_ip_addresses:
                if device_ip_address.interface_index == interface.if_index:
                    device_ip_address_detail = IpAddressDetail(
                            address = device_ip_address.address,
                            subnet_mask = device_ip_address.subnet_mask
                            )
                    ip_addresses.append(device_ip_address_detail)

            device_interface_detail = InterfaceDetail(
                    if_index = interface.if_index,
                    description = interface.description,
                    interface_type = interface.interface_type,
                    mtu = interface.mtu,
                    speed = interface.speed,
                    mac_address = interface.mac_address,
                    admin_status = interface.admin_status,
                    oper_status = interface.oper_status,
                    ip_addresses = ip_addresses
                    )

            interface_details.append(device_interface_detail)

        device_routes = self.route.get_by_device(device_id)
        route_details: list[RouteDetail] = []
        for device_route in device_routes:
            route = RouteDetail(
                    interface_index = device_route.interface_index,
                    destination = device_route.destination,
                    subnet_mask = device_route.subnet_mask,
                    next_hop = device_route.next_hop,
                    route_type = device_route.route_type,
                    protocol = device_route.protocol,
                    age = device_route.age
                    )

            route_details.append(route)


        managed_device_detail = DeviceDetail(
                id = device.id,
                management_ip = device.management_ip,
                device_type = device.device_type,
                enabled = device.enabled,
                snmp_port = device.snmp_port,
                snmp_version = device.snmp_version,
                system = system_detail,
                interfaces = interface_details,
                routes = route_details
                )

        return managed_device_detail
