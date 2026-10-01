from .base_repository import BaseRepository
from ..models.managed_device import (
    ManagedDevice,
    CreateManagedDevice,
    UpdateManagedDevice,
)


class ManagedDeviceRepository(BaseRepository):

    def get_devices(self) -> list[ManagedDevice]:
        return BaseRepository.get_all(
            self,
            ManagedDevice,
            ManagedDevice.TABLE_NAME,
        )

    def get_device_by_id(self, device_id: int) -> ManagedDevice | None:
        return BaseRepository.get_by_id(
            self,
            device_id,
            ManagedDevice,
            ManagedDevice.TABLE_NAME,
        )

    def create_device(
        self,
        device: CreateManagedDevice,
    ) -> ManagedDevice | None:
        return BaseRepository.create(
            self,
            device,
            ManagedDevice,
            ManagedDevice.TABLE_NAME,
        )

    def update_device(
        self,
        device_id: int,
        data: UpdateManagedDevice,
    ) -> bool:
        return BaseRepository.update(
            self,
            device_id,
            data,
            ManagedDevice.TABLE_NAME,
        )

    def delete_device(self, device_id: int) -> bool:
        return BaseRepository.delete_by_id(
            self,
            device_id,
            ManagedDevice.TABLE_NAME,
        )
