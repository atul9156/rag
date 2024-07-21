from fastapi import HTTPException, Header
from database.utils import find_user_with_email_or_token
from database.models import User


async def get_current_user(authorization: str = Header(None)) -> User:
    if authorization is None:
        raise HTTPException(status_code=400, detail="User token is required")
    token = authorization.replace("Bearer ", "").strip()
    user = await find_user_with_email_or_token(token=token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
