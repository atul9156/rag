import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

Base = declarative_base()


class AsDictMixin:
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base, AsDictMixin):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True, nullable=False)
    email: str = Column(String, index=True, unique=True, nullable=False)
    token: str = Column(String, index=True, unique=True, nullable=False)

    @validates("token")
    def generate_token(self, key, value):
        if self.id is None and not value:
            return str(uuid.uuid4())
        return value

    def __repr__(self) -> str:
        return f"<User(name={self.name}, email={self.email}, token={self.token})>"


class Document(Base, AsDictMixin):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint('uploaded_by', 'name', name='unique_user_id_name'),
    )


    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True, nullable=False)
    path: str = Column(String, index=False, nullable=False)
    uploaded_by: int = Column(Integer, ForeignKey("users.id"))

    @validates("name")
    def validate_name(self, key, value):
        if not value.strip():
            raise ValueError("name field cannot be blank")
        return value

    @validates("path")
    def validate_path(self, key, value):
        if not value.strip():
            raise ValueError("path field cannot be blank")
        return value
