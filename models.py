from sync_db import Base
from sqlalchemy import (Column, Integer, String,
                        TIMESTAMP, text, ForeignKey, Boolean)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telegram = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    container = relationship('Container', back_populates='user')


class Container(Base):
    __tablename__ = 'container'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    document_path = Column(String, nullable=False)

    user = relationship('User', back_populates='container')

