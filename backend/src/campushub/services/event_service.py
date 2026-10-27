from campushub.models.event import EventCandidate, EventCreate
from campushub.repositories.snmp_ip_address_repository import SnmpIpAddressRepository
from campushub.repositories.snmp_route_repository import SnmpRouteRepository
from ..repositories.snmp_interface_repository import SnmpInterfaceRepository
from ..repositories.event_repository import EventRepository
from ..models.snmp_device_snapshot import SnmpDeviceSnapshot
from ..models.enums import EventSeverity, EventSource

class EventService():
    def detect_events(self, device_snapshot: SnmpDeviceSnapshot) -> None:
        device_id = device_snapshot.system.device_id
        interface_repository = SnmpInterfaceRepository()
        ip_address_repository = SnmpIpAddressRepository()
        route_repository = SnmpRouteRepository()
        event_repository = EventRepository()


        snapshot_interfaces = device_snapshot.interfaces
        old_interfaces = interface_repository.get_by_device(device_id)

        detected_events = self.detect_interfaces_changes(old_interfaces, snapshot_interfaces, device_id)

        snapshot_ip_addresses = device_snapshot.ip_addresses
        old_ip_addresses = ip_address_repository.get_by_device(device_id)

        ip_address_events = self.detect_ip_changes(old_ip_addresses, snapshot_ip_addresses, device_id)

        detected_events.extend(ip_address_events)

        snapshot_routes = device_snapshot.routes
        old_routes = route_repository.get_by_device(device_id)

        route_events = self.detect_route_changes(old_routes, snapshot_routes, device_id)

        detected_events.extend(route_events)



    def detect_interfaces_changes(self, old_interfaces, new_interfaces, device_id) -> list[EventCandidate]:
        detected_events: list[EventCandidate] = []
        interfaces = {old_interface.if_index: old_interface for old_interface in old_interfaces}
        for snapshot_interface in new_interfaces:
            new_if_index = snapshot_interface.if_index
            old_interface = interfaces.get(new_if_index)
            if old_interface is not None:
                if snapshot_interface.oper_status == 2 and old_interface.oper_status == 1:
                    event = EventCandidate(
                            device_id=device_id,
                            interface_index=new_if_index,
                            event_type="interface_down",
                            source=EventSource.SNMP_POLL,
                            message=f"{snapshot_interface.description} down"
                            )
                    detected_events.append(event)
                elif snapshot_interface.oper_status == 1 and old_interface.oper_status == 2:
                     event = EventCandidate(
                            device_id=device_id,
                            interface_index=new_if_index,
                            event_type="interface_up",
                            source=EventSource.SNMP_POLL,
                            message=f"{snapshot_interface.description} up"
                            )
                     detected_events.append(event)

                if snapshot_interface.admin_status == 2 and old_interface.admin_status == 1:
                    event = EventCandidate(
                            device_id=device_id,
                            interface_index=new_if_index,
                            event_type="interface_admin_down",
                            source=EventSource.SNMP_POLL,
                            message=f"{snapshot_interface.description} administratively down"
                            )
                    detected_events.append(event)
                elif snapshot_interface.admin_status == 1 and old_interface.admin_status == 2:
                    event = EventCandidate(
                            device_id=device_id,
                            interface_index=new_if_index,
                            event_type="interface_admin_up",
                            source=EventSource.SNMP_POLL,
                            message=f"{snapshot_interface.description} administratively up"
                            )
                    detected_events.append(event)



        return detected_events

    def detect_ip_changes(self, old_ip_addresses, new_ip_addresses, device_id) -> list[EventCandidate]:
        detected_events: list[EventCandidate] = []
        old_ips = {
                (old_ip_address.interface_index, old_ip_address.address)
                for old_ip_address in old_ip_addresses
                }

        new_ips = {
                (new_ip_address.interface_index, new_ip_address.address)
                for new_ip_address in new_ip_addresses
                }

        removed_ips = old_ips - new_ips
        added_ips = new_ips - old_ips

        for interface_index, address in removed_ips:
            event = EventCandidate(
                    device_id=device_id,
                    interface_index=interface_index,
                    ip_address=address,
                    event_type="ip_address_removed",
                    source=EventSource.SNMP_POLL,
                    message=f"{address} removed from Interface {interface_index}"
                    )

            detected_events.append(event)

        for interface_index, address in added_ips:
            event = EventCandidate(
                    device_id=device_id,
                    interface_index=interface_index,
                    ip_address=address,
                    event_type="ip_address_added",
                    source=EventSource.SNMP_POLL,
                    message=f"{address} added to Interface {interface_index}"
                    )

            detected_events.append(event)

        return detected_events

    def detect_route_changes(self, old_routes, new_routes, device_id) -> list[EventCandidate]:
        detected_events: list[EventCandidate] = []
        old_route_keys = {
            (
                old_route.interface_index,
                old_route.destination,
                old_route.subnet_mask,
                old_route.next_hop
            ): old_route
            for old_route in old_routes
        }

        new_route_keys = {
            (
                new_route.interface_index,
                new_route.destination,
                new_route.subnet_mask,
                new_route.next_hop
            ): new_route
            for new_route in new_routes
        }

        removed_routes = old_route_keys.keys() - new_route_keys.keys()
        added_routes = new_route_keys.keys() - old_route_keys.keys()


        for removed_route in removed_routes:
            route_obj = old_route_keys[removed_route]

            event = EventCandidate(
                    device_id=device_id,
                    interface_index=route_obj.interface_index,
                    route=route_obj,
                    event_type="route_removed",
                    source=EventSource.SNMP_POLL,
                    message=(
                        f"Route removed: {route_obj.destination} "
                        f"(mask: {route_obj.subnet_mask}) "
                        f"via {route_obj.next_hop}, "
                        f"interface {route_obj.interface_index}"
                        )
                    )

            detected_events.append(event)

        for added_route in added_routes:
            route_obj = new_route_keys[added_route]

            event = EventCandidate(
                    device_id=device_id,
                    interface_index=route_obj.interface_index,
                    route=route_obj,
                    event_type="route_added",
                    source=EventSource.SNMP_POLL,
                    message=(
                        f"Route added: {route_obj.destination} "
                        f"(mask: {route_obj.subnet_mask}) "
                        f"via {route_obj.next_hop}, "
                        f"interface {route_obj.interface_index}"
                        )
                    )

            detected_events.append(event)

        return detected_events
