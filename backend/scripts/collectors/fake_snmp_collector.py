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
    def __init__(self, interval: int = 15) -> None:
        self.ingest: SnmpIngestService = SnmpIngestService()
        self.device_repository: ManagedDeviceRepository = ManagedDeviceRepository()

        self.interval: int = interval
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
                oper_status=random.choice([1, 1, 1, 1, 2]),
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
                    oper_status=random.choice([
                        1,
                        1,
                        1,
                        1,
                        1,
                        2,
                    ]),
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
                oper_status=random.choice([1, 1, 1, 1, 1, 2]),
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
                oper_status=random.choice([1, 1, 1, 1, 2]),
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

    def simulate_device(self, device_id: int) -> SnmpDeviceSnapshot:
        config = self.get_config(device_id)

        match config["device_type"]:
            case DeviceType.ROUTER:
                return self.simulate_router(device_id)

            case DeviceType.SWITCH:
                return self.simulate_switch(device_id)

            case DeviceType.SERVER:
                return self.simulate_server(device_id)

            case DeviceType.CLIENT:
                return self.simulate_client(device_id)

            case _:
                raise RuntimeError("Unsupported fake device type")

    def run(self) -> None:
        self.ensure_devices()
        self.running = True

        print(
            f"Fake SNMP collector started "
            f"(interval: {self.interval}s)"
        )

        try:
            while self.running:
                for management_ip, device_id in self.device_ids.items():
                    snapshot = self.simulate_device(device_id)

                    self.ingest.process_snapshot(snapshot)

                    print(
                        f"{snapshot.system.name} "
                        f"({management_ip}) | "
                        f"uptime={snapshot.system.uptime} | "
                        f"interfaces="
                        f"{[interface.oper_status for interface in snapshot.interfaces]}"
                    )

                print("-" * 70)
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nStopping fake SNMP collector...")
            self.stop()

    def stop(self) -> None:
        self.running = False
        print("Fake SNMP collector stopped")


if __name__ == "__main__":
    collector = FakeSnmpCollector(interval=15)
    collector.run()
