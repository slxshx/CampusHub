from campushub.models.user import User, CreateUser, UpdateUser
from ..repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def get_all_users(self) -> list[User]:
        return self.get_all(User, User.TABLE_NAME)

    def get_user_by_id(self, entity_id: int) -> User | None:
        return self.get_by_id(entity_id, User, User.TABLE_NAME)

    def create_user(self, create_user: CreateUser) -> User | None:
        return self.create(create_user, User, User.TABLE_NAME)

    def update_user(self, entity_id: int, update_user: UpdateUser) -> bool:
        return self.update(entity_id, update_user, User.TABLE_NAME)

    def delete_user(self, entity_id: int) -> bool:
        return self.delete_by_id(entity_id, User.TABLE_NAME)




