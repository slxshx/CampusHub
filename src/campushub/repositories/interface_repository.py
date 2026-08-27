from campushub.models.interface import Interface, CreateInterface, UpdateInterface
from ..repositories.base_repository import BaseRepository

class InterfaceRepository(BaseRepository):
    def get_all_interfaces(self) -> list[Interface]:
        return self.get_all(Interface, Interface.TABLE_NAME)

    def get_interface_by_id(self, entity_id: int) -> Interface | None:
        return self.get_by_id(entity_id, Interface, Interface.TABLE_NAME)

    def create_interface(self, create_interface: CreateInterface) -> Interface | None:
        return self.create(create_interface, Interface, Interface.TABLE_NAME)

    def update_interface(self, entity_id: int, update_interface: UpdateInterface) -> bool:
        return self.update(entity_id, update_interface, Interface.TABLE_NAME)

    def delete_interface(self, entity_id: int) -> bool:
        return self.delete_by_id(entity_id, Interface.TABLE_NAME)





