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
        self.uptime: int = 0
        self.device_id: int | None = None

    def ensure_device(self) -> None:
        devices = self.device_repository.get_devices()

        if devices:
            self.device_id = devices[0].id
            return

        device = CreateManagedDevice(
            management_ip=ip_address("192.168.10.1"),
            device_type=DeviceType.ROUTER,
            enabled=True,
            snmp_port=161,
            snmp_version=SnmpVersion.V2C,
        )

        created_device = self.device_repository.create_device(device)

        if created_device is None:
            raise RuntimeError("Could not create fake managed device")

        self.device_id = created_device.id

    def simulate_data(self) -> SnmpDeviceSnapshot:
        if self.device_id is None:
            raise RuntimeError("Fake device has not been initialized")

        self.uptime += self.interval

        interface_1_status = 1

        # Interface 2 fällt gelegentlich aus.
        interface_2_status = random.choice([
            1,
            1,
            1,
            1,
            2,
        ])

        system = SnmpSystem(
            device_id=self.device_id,
            description="Cisco 1841 Fake SNMP Router",
            object_id="1.3.6.1.4.1.9.1.1",
            uptime=self.uptime,
            name="CampusHub-Router-01",
            location="Campus 1",
        )

        interfaces = [
            SnmpInterface(
                device_id=self.device_id,
                if_index=1,
                description="FastEthernet0/0",
                interface_type=6,
                mtu=1500,
                speed=100_000_000,
                mac_address="00:11:22:33:44:55",
                admin_status=1,
                oper_status=interface_1_status,
            ),
            SnmpInterface(
                device_id=self.device_id,
                if_index=2,
                description="FastEthernet0/1",
                interface_type=6,
                mtu=1500,
                speed=100_000_000,
                mac_address="00:11:22:33:44:66",
                admin_status=1,
                oper_status=interface_2_status,
            ),
        ]

        ip_addresses = [
            SnmpIpAddress(
                device_id=self.device_id,
                interface_index=1,
                address=ip_address("192.168.10.1"),
                subnet_mask=ip_address("255.255.255.0"),
            ),
            SnmpIpAddress(
                device_id=self.device_id,
                interface_index=2,
                address=ip_address("192.168.20.1"),
                subnet_mask=ip_address("255.255.255.0"),
            ),
        ]

        routes = [
            SnmpRoute(
                device_id=self.device_id,
                interface_index=1,
                destination=ip_address("192.168.10.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 60),
            ),
            SnmpRoute(
                device_id=self.device_id,
                interface_index=2,
                destination=ip_address("192.168.20.0"),
                subnet_mask=ip_address("255.255.255.0"),
                next_hop=ip_address("0.0.0.0"),
                route_type=3,
                protocol=2,
                age=random.randint(0, 60),
            ),
        ]

        return SnmpDeviceSnapshot(
            system=system,
            interfaces=interfaces,
            ip_addresses=ip_addresses,
            routes=routes,
        )

    def run(self) -> None:
        self.ensure_device()
        self.running = True

        print(
            f"Fake SNMP collector started "
            f"(interval: {self.interval}s, device_id: {self.device_id})"
        )

        try:
            while self.running:
                snapshot = self.simulate_data()

                self.ingest.process_snapshot(snapshot)

                print(
                    f"Snapshot ingested | "
                    f"uptime={snapshot.system.uptime} | "
                    f"interfaces="
                    f"{[interface.oper_status for interface in snapshot.interfaces]}"
                )

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
