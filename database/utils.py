from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from .connection import SessionLocal
from .models import User, Document


async def create_user(name: str, email: str, token: Optional[str] = None) -> User:
    async with SessionLocal() as session:
        user = User(name=name, email=email, token=token)
        session.add(user)
        await session.commit()
        return user


async def find_user_with_email_or_token(email: Optional[str] = None, token: Optional[str] = None) -> Optional[User]:
    if not email and not token:
        raise KeyError("Atleast one of email of token must be passed")
    user = None
    async with SessionLocal() as session:
        try:
            if email:
                query = await session.execute(select(User).filter(User.email == email))
            else:
                query = await session.execute(select(User).filter(User.token == token))
            user = query.scalars().first()
        except NoResultFound:
            pass
    return user


async def find_user_with_email_and_token(email: str, token: str) -> Optional[User]:
    if not email and not token:
        raise KeyError("Atleast one of email of token must be passed")
    async with SessionLocal() as session:
        try:
            query = await session.execute(select(User).filter(User.email == email, User.token == token))
            return query.scalars().first()
        except NoResultFound:
            return None


async def update_user(id: int, name: str, email: str):
    async with SessionLocal() as session:
        user = await session.get(User, id)
        if user:
            user.name = name
            user.email = email
            await session.commit()


async def create_document(file_name: str, file_path: str, user_id: int) -> Document:
    async with SessionLocal() as session:
        document = Document(name=file_name, path=file_path, uploaded_by=user_id)
        session.add(document)
        await session.commit()
        return document


async def get_documents_by_user(
    user_id: int, limit: Optional[int] = None, offset: Optional[int] = None
) -> Optional[List[Document]]:
    async with SessionLocal() as session:
        query = select(Document).filter(Document.uploaded_by == user_id)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)
        query = query.order_by(Document.id)

        result = await session.execute(query)
        return result.scalars().all()


async def get_document_by_name_or_id(
    user_id: int, name: Optional[str] = None, doc_id: Optional[int] = None
) -> Optional[Document]:
    if not name and not id:
        raise KeyError("At least one of name or id is required")

    async with SessionLocal() as session:
        if name:
            query = await session.execute(select(Document).filter(Document.uploaded_by == user_id).filter(Document.name == name))
        else:
            query = await session.execute(select(Document).filter(Document.uploaded_by == user_id).filter(Document.id == doc_id))

        return query.scalars().first()


async def delete_documents_by_user(user_id: int):
    async with SessionLocal() as session:
        query = delete(Document).where(Document.uploaded_by == user_id)
        await session.execute(query)
        await session.commit()
