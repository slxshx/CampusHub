import argparse
import random
import time
from ipaddress import ip_address

from campushub.models.managed_device import CreateManagedDevice
from campushub.models.enums import DeviceType, SnmpVersion
from campushub.models.snmp_system import SnmpSystem
from campushub.models.snmp_interface import SnmpInterface
from campushub.models.snmp_ipaddress import SnmpIpAddress
from campushub.models.snmp_route import SnmpRoute
from campushub.models.snmp_device_snapshot import SnmpDeviceSnapshot

from campushub.repositories.managed_device_repository import ManagedDeviceRepository
from campushub.services.snmp_ingest_service import SnmpIngestService


class FakeSnmpCollector:
    def __init__(self, interval: int = 15, cycles: int | None = None) -> None:
        self.ingest: SnmpIngestService = SnmpIngestService()
        self.device_repository: ManagedDeviceRepository = ManagedDeviceRepository()

        self.interval: int = interval
        self.cycles: int | None = cycles
        self.cycle: int = 0
        self.running: bool = False

        self.device_ids: dict[str, int] = {}
        self.uptimes: dict[int, int] = {}

        self.devices = [
            {
                "management_ip": "192.168.10.1",
                "device_type": DeviceType.ROUTER,
                "name": "CampusHub-Router-01",
                "description": "Cisco 1841 Fake Router",
                "object_id": "1.3.6.1.4.1.9.1.1",
                "location": "Serverraum",
            },
            {
                "management_ip": "192.168.10.2",
                "device_type": DeviceType.SWITCH,
                "name": "CampusHub-Switch-01",
                "description": "Cisco Catalyst Fake Switch",
                "object_id": "1.3.6.1.4.1.9.1.516",
                "location": "Campus 1 - Etage 1",
            },
            {
                "management_ip": "192.168.10.10",
                "device_type": DeviceType.SERVER,
                "name": "CampusHub-Server-01",
                "description": "Ubuntu Fake Application Server",
                "object_id": "1.3.6.1.4.1.8072.3.2.10",
                "location": "Serverraum",
            },
            {
                "management_ip": "192.168.10.20",
                "device_type": DeviceType.CLIENT,
                "name": "CampusHub-Client-01",
                "description": "Fake Workstation",
                "object_id": "1.3.6.1.4.1.8072.3.2.10",
                "location": "Raum 101",
            },
        ]

    def ensure_devices(self) -> None:
        existing_devices = self.device_repository.get_devices()

        existing_by_ip = {
            str(device.management_ip): device
            for device in existing_devices
        }

        for config in self.devices:
            management_ip = config["management_ip"]

            if management_ip in existing_by_ip:
                device = existing_by_ip[management_ip]
                self.device_ids[management_ip] = device.id
                self.uptimes[device.id] = random.randint(10_000, 100_000)
                continue

            new_device = CreateManagedDevice(
                management_ip=ip_address(management_ip),
                device_type=config["device_type"],
                enabled=True,
                snmp_port=161,
                snmp_version=SnmpVersion.V2C,
            )

            created_device = self.device_repository.create_device(new_device)

            if created_device is None:
                raise RuntimeError(
                    f"Could not create fake device {management_ip}"
                )

            self.device_ids[management_ip] = created_device.id
            self.uptimes[created_device.id] = random.randint(10_000, 100_000)

    def simulate_router(self, device_id: int) -> SnmpDeviceSnapshot:
        interfaces = [
            SnmpInterface(
                device_id=device_id,
                if_index=1,
                description="FastEthernet0/0",
                interface_type=6,
                mtu=1500,
                speed=100_000_000,
                mac_address="00:11:22:33:44:01",
                admin_status=1,
                oper_status=1,
            ),
            SnmpInterface(
                device_id=device_id,
                if_index=2,
                description="FastEthernet0/1",
                interface_type=6,
                mtu=1500,
                speed=100_000_000,
                mac_address="00:11:22:33:44:02",
                admin_status=1,
                oper_status=1,
            ),
        ]

        ip_addresses = [
            SnmpIpAddress(
                device_id=device_id,
                interface_index=1,
                address=ip_address("192.168.10.1"),
                subnet_mask=ip_address("255.255.255.0"),
            ),
            SnmpIpAddress(
                device_id=device_id,
                interface_index=2,
                address=ip_address("192.168.20.1"),
                subnet_mask=ip_address("255.255.255.0"),
            ),
        ]

        routes = [
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("192.168.10.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 120),
            ),
            SnmpRoute(
                device_id=device_id,
                interface_index=2,
                destination=ip_address("192.168.20.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 120),
            ),
        ]

        return self.build_snapshot(
            device_id=device_id,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def simulate_switch(self, device_id: int) -> SnmpDeviceSnapshot:
        interfaces: list[SnmpInterface] = []

        interfaces.append(
            SnmpInterface(
                device_id=device_id,
                if_index=1,
                description="Vlan1",
                interface_type=53,
                mtu=1500,
                speed=1_000_000_000,
                mac_address="00:22:33:44:55:01",
                admin_status=1,
                oper_status=1,
            )
        )

        for port in range(1, 9):
            interfaces.append(
                SnmpInterface(
                    device_id=device_id,
                    if_index=port + 1,
                    description=f"GigabitEthernet0/{port}",
                    interface_type=6,
                    mtu=1500,
                    speed=1_000_000_000,
                    mac_address=f"00:22:33:44:55:{port + 1:02X}",
                    admin_status=1,
                    oper_status=1,
                )
            )

        ip_addresses = [
            SnmpIpAddress(
                device_id=device_id,
                interface_index=1,
                address=ip_address("192.168.10.2"),
                subnet_mask=ip_address("255.255.255.0"),
            )
        ]

        routes = [
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("192.168.10.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 120),
            )
        ]

        return self.build_snapshot(
            device_id=device_id,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def simulate_server(self, device_id: int) -> SnmpDeviceSnapshot:
        interfaces = [
            SnmpInterface(
                device_id=device_id,
                if_index=1,
                description="eth0",
                interface_type=6,
                mtu=1500,
                speed=1_000_000_000,
                mac_address="00:33:44:55:66:01",
                admin_status=1,
                oper_status=1,
            ),
            SnmpInterface(
                device_id=device_id,
                if_index=2,
                description="lo",
                interface_type=24,
                mtu=65536,
                speed=10_000_000,
                mac_address=None,
                admin_status=1,
                oper_status=1,
            ),
        ]

        ip_addresses = [
            SnmpIpAddress(
                device_id=device_id,
                interface_index=1,
                address=ip_address("192.168.10.10"),
                subnet_mask=ip_address("255.255.255.0"),
            ),
            SnmpIpAddress(
                device_id=device_id,
                interface_index=2,
                address=ip_address("127.0.0.1"),
                subnet_mask=ip_address("255.0.0.0"),
            ),
        ]

        routes = [
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("192.168.10.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 120),
            ),
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("0.0.0.0"),
                subnet_mask=ip_address("0.0.0.0"),
                next_hop=ip_address("192.168.10.1"),
                route_type=4,
                protocol=2,
                age=random.randint(0, 120),
            ),
        ]

        return self.build_snapshot(
            device_id=device_id,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def simulate_client(self, device_id: int) -> SnmpDeviceSnapshot:
        interfaces = [
            SnmpInterface(
                device_id=device_id,
                if_index=1,
                description="Ethernet",
                interface_type=6,
                mtu=1500,
                speed=1_000_000_000,
                mac_address="00:44:55:66:77:01",
                admin_status=1,
                oper_status=1,
            )
        ]

        ip_addresses = [
            SnmpIpAddress(
                device_id=device_id,
                interface_index=1,
                address=ip_address("192.168.10.20"),
                subnet_mask=ip_address("255.255.255.0"),
            )
        ]

        routes = [
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("192.168.10.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 120),
            ),
            SnmpRoute(
                device_id=device_id,
                interface_index=1,
                destination=ip_address("0.0.0.0"),
                subnet_mask=ip_address("0.0.0.0"),
                next_hop=ip_address("192.168.10.1"),
                route_type=4,
                protocol=2,
                age=random.randint(0, 120),
            ),
        ]

        return self.build_snapshot(
            device_id=device_id,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def apply_scenario(self, snapshot: SnmpDeviceSnapshot, phase: int) -> None:
        """Apply a deterministic disturbance to an otherwise healthy snapshot.

        The states deliberately last at least two polls. Therefore the event
        detector can demonstrate that it emits changes, not repeated alarms.
        """
        device_type = self.get_config(snapshot.system.device_id)["device_type"]

        # Router: operational link loss causes the associated route to vanish.
        # This tests interface_down + route_removed correlation (score 45).
        if device_type == DeviceType.ROUTER and phase in (2, 3):
            for interface in snapshot.interfaces:
                if interface.if_index == 2:
                    interface.oper_status = 2
            snapshot.routes = [
                route for route in snapshot.routes if route.interface_index != 2
            ]

        # Switch: deliberate administrative shutdown; both status events fire.
        if device_type == DeviceType.SWITCH and phase in (6, 7):
            for interface in snapshot.interfaces:
                if interface.if_index == 2:
                    interface.admin_status = 2
                    interface.oper_status = 2

        # Server: a vanished IPv4 default route is CRITICAL (score 85).
        if device_type == DeviceType.SERVER and phase in (10, 11):
            snapshot.routes = [
                route for route in snapshot.routes
                if not (
                    route.destination == ip_address("0.0.0.0")
                    and route.subnet_mask == ip_address("0.0.0.0")
                )
            ]

        # Client: remove and later restore an assigned IP address.
        if device_type == DeviceType.CLIENT and phase in (13,):
            snapshot.ip_addresses = []

        # Server: default-route loss AND the corresponding interface fails.
        # Correlation + default-route modifier produces HIGH (score 70).
        if device_type == DeviceType.SERVER and phase in (16, 17):
            for interface in snapshot.interfaces:
                if interface.if_index == 1:
                    interface.oper_status = 2
            snapshot.routes = [
                route for route in snapshot.routes
                if not (
                    route.destination == ip_address("0.0.0.0")
                    and route.subnet_mask == ip_address("0.0.0.0")
                )
            ]

    def seed_baseline(self) -> None:
        """Initialize only the four fake devices, without generating events.

        This intentionally resets their current SNMP snapshots for a
        reproducible demonstration. It does not clear existing event history.
        """
        self.ensure_devices()
        print("Seeding healthy fake-device baseline (without event detection)...")
        for management_ip, device_id in self.device_ids.items():
            snapshot = self.simulate_device(device_id, phase=0)
            self.ingest.process_snapshot(snapshot, detect_events=False)
            print(f"  Baseline: {snapshot.system.name} ({management_ip})")
        print("Baseline complete.")

    def build_snapshot(
        self,
        device_id: int,
        interfaces: list[SnmpInterface],
        ip_addresses: list[SnmpIpAddress],
        routes: list[SnmpRoute],
    ) -> SnmpDeviceSnapshot:
        config = self.get_config(device_id)

        self.uptimes[device_id] += self.interval

        system = SnmpSystem(
            device_id=device_id,
            description=config["description"],
            object_id=config["object_id"],
            uptime=self.uptimes[device_id],
            name=config["name"],
            location=config["location"],
        )

        return SnmpDeviceSnapshot(
            system=system,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def get_config(self, device_id: int):
        for config in self.devices:
            management_ip = config["management_ip"]

            if self.device_ids.get(management_ip) == device_id:
                return config

        raise RuntimeError(
            f"No fake configuration found for device {device_id}"
        )

    def simulate_device(self, device_id: int, phase: int | None = None) -> SnmpDeviceSnapshot:
        config = self.get_config(device_id)
        if phase is None:
            phase = self.cycle % 20

        match config["device_type"]:
            case DeviceType.ROUTER:
                snapshot = self.simulate_router(device_id)
            case DeviceType.SWITCH:
                snapshot = self.simulate_switch(device_id)
            case DeviceType.SERVER:
                snapshot = self.simulate_server(device_id)
            case DeviceType.CLIENT:
                snapshot = self.simulate_client(device_id)
            case _:
                raise RuntimeError("Unsupported fake device type")

        self.apply_scenario(snapshot, phase)
        return snapshot

    def run(self) -> None:
        # Always reset fake-device snapshot state for a reproducible demo.
        # Requires detect_events=False support in SnmpIngestService.
        self.seed_baseline()
        self.running = True
        print(f"Fake SNMP collector started (interval: {self.interval}s)")
        print("Demo repeats every 20 cycles; Ctrl+C stops it.")

        try:
            while self.running and (self.cycles is None or self.cycle < self.cycles):
                phase = self.cycle % 20
                print(f"\n[cycle {self.cycle + 1}, scenario phase {phase}/19]")
                for management_ip, device_id in self.device_ids.items():
                    snapshot = self.simulate_device(device_id, phase=phase)
                    result = self.ingest.process_snapshot(snapshot)
                    event_count = len(result.events) if result is not None else 0
                    print(
                        f"  {snapshot.system.name} ({management_ip}) | "
                        f"interfaces={[i.oper_status for i in snapshot.interfaces]} | "
                        f"ips={len(snapshot.ip_addresses)} | "
                        f"routes={len(snapshot.routes)} | "
                        f"classified_events={event_count}"
                    )
                    if result is not None and result.events:
                        print(
                            f"    Candidates: {result.candidate_count} | "
                            f"correlated: {result.correlated_count} | "
                            f"classifier: {result.processing_time_ms:.3f} ms"
                        )
                        for event in result.events:
                            print(
                                f"    [{event.severity.value.upper()}] "
                                f"{event.event_type.value}: {event.message}"
                            )

                self.cycle += 1
                if self.running and (self.cycles is None or self.cycle < self.cycles):
                    time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nStopping fake SNMP collector...")
        finally:
            self.stop()

    def stop(self) -> None:
        self.running = False
        print("Fake SNMP collector stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CampusHub deterministic SNMP demo")
    parser.add_argument("--interval", type=int, default=15, help="Seconds per poll")
    parser.add_argument("--cycles", type=int, default=None, help="Stop after N polls")
    parser.add_argument("--seed-only", action="store_true", help="Only seed baseline")
    args = parser.parse_args()
    if args.interval < 0 or (args.cycles is not None and args.cycles < 1):
        parser.error("--interval must be >= 0 and --cycles must be >= 1")

    collector = FakeSnmpCollector(interval=args.interval, cycles=args.cycles)
    if args.seed_only:
        collector.seed_baseline()
    else:
        collector.run()

