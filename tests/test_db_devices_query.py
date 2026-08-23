from campushub.repositories.device_repository import DeviceRepository
repo = DeviceRepository()
result = DeviceRepository.get_all_devices(repo)

print(result)
