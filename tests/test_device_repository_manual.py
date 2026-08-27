from campushub.models.device import CreateDevice, UpdateDevice
from campushub.repositories.device_repository import DeviceRepository


def run_smoke_test():
    repository = DeviceRepository()

    print("=== CREATE ===")

    create_device = CreateDevice(
        hostname="smoke-test-switch",
        description="Device Repository Smoke Test",
        device_type="switch",
        location="test-lab",
    )

    created_device = repository.create_device(create_device)

    print(created_device)

    if created_device is None:
        print("CREATE FAILED")
        return

    device_id = created_device.id

    print("\n=== GET BY ID ===")

    fetched_device = repository.get_device_by_id(device_id)

    print(fetched_device)

    print("\n=== UPDATE ===")

    update_device = UpdateDevice(
        location="updated-test-lab"
    )

    update_result = repository.update_device(
        device_id,
        update_device
    )

    print(f"Update result: {update_result}")

    print("\n=== GET AFTER UPDATE ===")

    updated_device = repository.get_device_by_id(device_id)

    print(updated_device)

    print("\n=== GET ALL ===")

    devices = repository.get_all_devices()

    for device in devices:
        print(device)

    print("\n=== DELETE ===")

    delete_result = repository.delete_device(device_id)

    print(f"Delete result: {delete_result}")

    print("\n=== GET AFTER DELETE ===")

    deleted_device = repository.get_device_by_id(device_id)

    print(deleted_device)

    print("\n=== NEGATIVE TESTS ===")

    missing_device = repository.get_device_by_id(999999)
    print(f"Missing device: {missing_device}")

    missing_delete = repository.delete_device(999999)
    print(f"Delete missing device: {missing_delete}")

    print("\n=== SMOKE TEST FINISHED ===")


if __name__ == "__main__":
    run_smoke_test()
