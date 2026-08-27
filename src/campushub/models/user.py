from typing import ClassVar
from pydantic import BaseModel

class User(BaseModel):
    TABLE_NAME: ClassVar[str] = "users"

    id: int
    username: str
    password_hash: str
    role: str

class CreateUser(BaseModel):
    TABLE_NAME: ClassVar[str] = "users"

    username: str
    password_hash: str
    role: str

class UpdateUser(BaseModel):
    TABLE_NAME: ClassVar[str] = "users"

    username: str | None = None
    password_hash: str | None = None
    role: str | None = None
