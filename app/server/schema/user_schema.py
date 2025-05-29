from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from enum import Enum

password = str()
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    password: str
    role: UserRole = Field(default=UserRole.USER)
    token: str
    
class UserPublic(SQLModel):
    username: str
    email: EmailStr
    role: UserRole

