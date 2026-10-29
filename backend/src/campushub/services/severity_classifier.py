from time import perf_counter

from ipaddress import IPv4Address
from typing import ClassVar


from campushub.models.classification_result import ClassificationResult
from campushub.models.event import EventCandidate, EventCreate
from campushub.models.enums import EventSeverity, EventType, ModifierType
from campushub.models.snmp_interface import SnmpInterface

class SeverityClassifier():
    BASE_SCORES: ClassVar[dict[EventType, int]] = {
            EventType.INTERFACE_DOWN: 65,
            EventType.INTERFACE_UP: 10,
            EventType.INTERFACE_ADMIN_DOWN: 40,
            EventType.INTERFACE_ADMIN_UP: 10,
            EventType.IP_ADDRESS_REMOVED: 45,
            EventType.IP_ADDRESS_ADDED: 15,
            EventType.ROUTE_REMOVED: 60, 
            EventType.ROUTE_ADDED: 15
            }

    CONTEXT_MODIFIERS: ClassVar[dict[ModifierType, int]] = {
            ModifierType.ADMINISTRATIVE_SHUTDOWN: -40,
            ModifierType.ROUTE_REMOVED_INTERFACE_DOWN: -15,
            ModifierType.DEFAULT_ROUTE_REMOVED: 25
            }

    def get_severity_level(self, score: int) -> EventSeverity:
        if score < 0:
            score = 0

        if score > 100:
            score = 100

        if score < 20:
            return EventSeverity.INFO
        elif score < 50:
            return EventSeverity.LOW
        elif score < 70:
            return EventSeverity.WARNING
        elif score < 80: 
            return EventSeverity.HIGH
        else: 
            return EventSeverity.CRITICAL

    def analyze_candidates(self, candidates:list[EventCandidate], snapshot_interfaces: list[SnmpInterface]) -> ClassificationResult:
        timer_start = perf_counter()
        candidates_count = len(candidates)
        correlation_counter = 0
        create_events: list[EventCreate] = []
        interfaces: dict[int, SnmpInterface] = {}
        for snapshot_interface in snapshot_interfaces:
            interfaces[snapshot_interface.if_index] = snapshot_interface
        down_interfaces = set()
        for candidate in candidates:
            if candidate.event_type == EventType.INTERFACE_DOWN and candidate.interface_index is not None:
                down_interfaces.add((candidate.device_id, candidate.interface_index))

        for candidate in candidates:
            calculated_score = self.BASE_SCORES[candidate.event_type]
            if candidate.interface_index is not None:
                candidate_interface = interfaces.get(candidate.interface_index)
                if candidate_interface is not None:
                    if candidate.event_type == EventType.INTERFACE_DOWN and candidate_interface.admin_status == 2:
                        calculated_score += self.CONTEXT_MODIFIERS[ModifierType.ADMINISTRATIVE_SHUTDOWN]

            if candidate.event_type == EventType.ROUTE_REMOVED:
                if candidate.route is not None:
                    if candidate.route.destination == IPv4Address("0.0.0.0") and candidate.route.subnet_mask == IPv4Address("0.0.0.0"):
                        calculated_score += self.CONTEXT_MODIFIERS[ModifierType.DEFAULT_ROUTE_REMOVED]

                if candidate.interface_index is not None:
                    if (candidate.device_id, candidate.interface_index) in down_interfaces:
                        calculated_score += self.CONTEXT_MODIFIERS[ModifierType.ROUTE_REMOVED_INTERFACE_DOWN]
                        correlation_counter += 1

            event = EventCreate(
                    device_id=candidate.device_id,
                    interface_index=candidate.interface_index,
                    severity=self.get_severity_level(calculated_score),
                    event_type=candidate.event_type,
                    source=candidate.source,
                    message=candidate.message
                    )

            create_events.append(event)

        timer_end = perf_counter()
        processing_time_ms = (timer_end - timer_start) * 1000

        return ClassificationResult(
                events=create_events,
                candidate_count=candidates_count,
                correlated_count=correlation_counter,
                processing_time_ms=processing_time_ms
                )

        




