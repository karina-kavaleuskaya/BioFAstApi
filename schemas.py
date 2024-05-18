from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    email: str
    telegram: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password:str


class User(UserBase):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class ContainerBase(BaseModel):
    user_id: int

    class Config:
        from_attributes = True


class ContainerCreate(ContainerBase):
    pass


class Container(ContainerBase):
    id: int

    class Config:
        from_attributes = True
