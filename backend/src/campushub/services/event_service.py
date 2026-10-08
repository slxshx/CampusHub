from campushub.models.event import EventCreate
from ..repositories.snmp_interface_repository import SnmpInterfaceRepository
from ..repositories.event_repository import EventRepository
from ..models.snmp_device_snapshot import SnmpDeviceSnapshot
from ..models.enums import EventSeverity, EventSource

class EventService():
    def detect_events(self, device_snapshot: SnmpDeviceSnapshot) -> None:
        device_id = device_snapshot.system.device_id
        interface_repository = SnmpInterfaceRepository()
        event_repository = EventRepository()

        snapshot_interfaces = device_snapshot.interfaces
        old_interfaces = interface_repository.get_by_device(device_id)

        detected_events: list[EventCreate] = []
        for snapshot_interface in snapshot_interfaces:
            new_if_index = snapshot_interface.if_index
            
            for old_interface in old_interfaces:
                if new_if_index == old_interface.if_index:
                    if snapshot_interface.oper_status == 2 and old_interface.oper_status == 1:
                        event = EventCreate(
                                device_id=device_id,
                                interface_index=new_if_index,
                                severity=EventSeverity.WARNING,
                                event_type="interface_down",
                                source=EventSource.SNMP_POLL,
                                message=f"{snapshot_interface.description} down"
                                )
                        detected_events.append(event)
                    elif snapshot_interface.oper_status == 1 and old_interface.oper_status == 2:
                         event = EventCreate(
                                device_id=device_id,
                                interface_index=new_if_index,
                                severity=EventSeverity.INFO,
                                event_type="interface_up",
                                source=EventSource.SNMP_POLL,
                                message=f"{snapshot_interface.description} up"
                                )
                         detected_events.append(event)
        
        for detected_event in detected_events:
            event_repository.create_event(detected_event)

