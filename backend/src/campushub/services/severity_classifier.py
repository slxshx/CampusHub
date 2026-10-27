from ipaddress import IPv4Address
from typing import ClassVar

from campushub.models.event import EventCandidate, EventCreate
from campushub.models.enums import EventSeverity
from campushub.models.snmp_interface import SnmpInterface

class SeverityClassifier():
    BASE_SCORES: ClassVar[dict[str, int]] = {
            "interface_down": 65,
            "interface_up": 10,
            "interface_admin_down": 40,
            "interface_admin_up": 10,
            "ip_address_removed": 45,
            "ip_address_added": 15,
            "route_removed": 60, 
            "route_added": 15
            }

    CONTEXT_MODIFIERS: ClassVar[dict[str, int]] = {
            "administrative_shutdown": -40,
            "route_removed_interface_down": -15,
            "default_route_removed": 25
            }

    def get_severity_level(self, score: int) -> EventSeverity:
        if score < 0:
            score = 0

        if score > 100:
            score = 100

        if score < 20:
            return EventSeverity.INFO
        elif score < 40:
            return EventSeverity.LOW
        elif score < 70:
            return EventSeverity.WARNING
        else:
            return EventSeverity.CRITICAL


    def analyze_candidates(self, candidates:list[EventCandidate], snapshot_interfaces: list[SnmpInterface]) -> list[EventCreate]:
        create_events: list[EventCreate] = []
        interfaces: dict[int, SnmpInterface] = {}
        for snapshot_interface in snapshot_interfaces:
            interfaces[snapshot_interface.if_index] = snapshot_interface
        down_interfaces = set()
        for candidate in candidates:
            if candidate.event_type == "interface_down" and candidate.interface_index is not None:
                down_interfaces.add((candidate.device_id, candidate.interface_index))

        for candidate in candidates:
            calculated_score = self.BASE_SCORES[candidate.event_type]
            if candidate.interface_index is not None:
                candidate_interface = interfaces.get(candidate.interface_index)
                if candidate_interface is not None:
                    if candidate.event_type == 'interface_down' and candidate_interface.admin_status == 2:
                        calculated_score += self.CONTEXT_MODIFIERS['administrative_shutdown']

            if candidate.event_type == "route_removed":
                if candidate.route is not None:
                    if candidate.route.destination == IPv4Address("0.0.0.0") and candidate.route.subnet_mask == IPv4Address("0.0.0.0"):
                        calculated_score += self.CONTEXT_MODIFIERS["default_route_removed"]

                if candidate.interface_index is not None:
                    if (candidate.device_id, candidate.interface_index) in down_interfaces:
                        calculated_score += self.CONTEXT_MODIFIERS["route_removed_interface_down"]

            event = EventCreate(
                    device_id=candidate.device_id,
                    interface_index=candidate.interface_index,
                    severity=self.get_severity_level(calculated_score),
                    event_type=candidate.event_type,
                    source=candidate.source,
                    message=candidate.message
                    )

            create_events.append(event)

        return create_events




