import pytest
from pydantic import ValidationError

from campushub.models.user import CreateUser, UpdateUser


def test_create_user_with_valid_data():
    user = CreateUser(
        username="admin",
        password_hash="some-hash",
        role="admin",
    )

    assert user.username == "admin"
    assert user.password_hash == "some-hash"
    assert user.role == "admin"


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "password_hash": "some-hash",
            "role": "admin",
        },
        {
            "username": "admin",
            "role": "admin",
        },
        {
            "username": "admin",
            "password_hash": "some-hash",
        },
    ],
)
def test_create_user_without_required_field_fails(test_data):
    with pytest.raises(ValidationError):
        CreateUser(**test_data)


def test_update_user_one_parameter():
    update_user = UpdateUser(
        username="new-name"
    )

    data = update_user.model_dump(exclude_unset=True)

    assert data == {
        "username": "new-name"
    }


def test_update_user_multiple_parameters():
    update_user = UpdateUser(
        username="new-name",
        role="viewer",
    )

    data = update_user.model_dump(exclude_unset=True)

    assert data == {
        "username": "new-name",
        "role": "viewer",
    }


def test_update_user_without_parameters():
    update_user = UpdateUser()

    data = update_user.model_dump(exclude_unset=True)

    assert data == {}


def test_update_user_explicit_none():
    update_user = UpdateUser(
        role=None
    )

    data = update_user.model_dump(exclude_unset=True)

    assert data == {
        "role": None
    }
