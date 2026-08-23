from campushub.models.device import Device
from ..repositories.base_repository import BaseRepository

class DeviceRepository(BaseRepository):
    def get_all_devices(self):
        return self.get_all(
                Device,
                Device.TABLE_NAME
                )


