from campushub.models.device import Device, CreateDevice, UpdateDevice
from ..repositories.base_repository import BaseRepository

class DeviceRepository(BaseRepository):
    def get_all_devices(self) -> list[Device]:
        return self.get_all(Device, Device.TABLE_NAME)

    def get_device_by_id(self, entity_id: int) -> Device | None:
        return self.get_by_id(entity_id, Device, Device.TABLE_NAME)

    def create_device(self, create_device: CreateDevice) -> Device | None:
        return self.create(create_device, Device, Device.TABLE_NAME)

    def update_device(self, entity_id: int, update_device: UpdateDevice) -> bool:
        return self.update(entity_id, update_device, Device.TABLE_NAME)

    def delete_device(self, entity_id: int) -> bool:
        return self.delete_by_id(entity_id, Device.TABLE_NAME)



