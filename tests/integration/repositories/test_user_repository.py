from campushub.models.user import UpdateUser
from campushub.repositories.user_repository import UserRepository


def test_create_user(test_user):
    assert test_user.id is not None
    assert test_user.username == "fixture-user"
    assert test_user.password_hash == "fixture-hash"
    assert test_user.role == "user"


def test_get_all_users(test_user):
    repository = UserRepository()

    result = repository.get_all_users()

    assert isinstance(result, list)
    assert any(user.id == test_user.id for user in result)


def test_get_user_by_id(test_user):
    repository = UserRepository()

    result = repository.get_user_by_id(test_user.id)

    assert result is not None
    assert result.id == test_user.id


def test_update_user(test_user):
    repository = UserRepository()

    update_user = UpdateUser(
        username="updated-fixture-user",
        password_hash="updated-hash",
        role="admin",
    )

    result = repository.update_user(
        test_user.id,
        update_user,
    )

    assert result is True

    new_test_user = repository.get_user_by_id(test_user.id)

    assert new_test_user is not None
    assert new_test_user.username == "updated-fixture-user"
    assert new_test_user.password_hash == "updated-hash"
    assert new_test_user.role == "admin"


def test_delete_user(test_user):
    repository = UserRepository()

    result = repository.delete_user(test_user.id)

    assert result is True

    is_user_deleted = repository.get_user_by_id(test_user.id)

    assert is_user_deleted is None
