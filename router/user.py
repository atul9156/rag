from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from database.models import User
from .dependency import get_current_user
from database.utils import find_user_with_email_and_token, find_user_with_email_or_token, create_user, update_user
from pydantic import BaseModel

user_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    token: str


class RegisterRequest(BaseModel):
    name: str
    email: str


class SetUserDetailsRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


@user_router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest):
    """
    User login endpoint
    Returns:
        status code 200 if email and token found in the DB, 404 otherwise
    """
    email = login_request.email
    token = login_request.token
    user = await find_user_with_email_and_token(email=email, token=token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Login successful", "token": token}


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(register_request: RegisterRequest):
    """
    User registration endpoint
    Returns:
        - 201 response with serialized user object if user is created successfully
    """
    existing_user = await find_user_with_email_or_token(email=register_request.email)
    if existing_user:
        return existing_user.as_dict()
    new_user = await create_user(name=register_request.name, email=register_request.email)
    return new_user.as_dict()


@user_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(user: User = Depends(get_current_user)):
    """
    User logout endpoint
    Returns:
        - 200 response with a message indicating successful logout
    """

    return {"message": "Logout successful"}


@user_router.get("/user", status_code=status.HTTP_200_OK)
async def get_user_details(user: User = Depends(get_current_user)):
    """
    User get endpoint
    Returns:

    """
    return user.as_dict()


@user_router.put("/user", status_code=status.HTTP_200_OK)
async def set_user_details(set_user_details_request: SetUserDetailsRequest, user: User = Depends(get_current_user)):
    """
    User create/update endpoint
    Returns:
        - JSON response with updated user details
    """
    email = set_user_details_request.email
    name = set_user_details_request.name
    if not email and not name:
        raise HTTPException(status_code=400, detail="At least one of email or name must be provided")
    if email and email != user.email:
        existing_user = await find_user_with_email_or_token(email=email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email is already in use by another user")

    if (email and email != user.email) or (name and name != user.name):
        user.name = name or user.name
        user.email = email or user.email
        await update_user(user.id, user.name, user.email)

    return user.as_dict()
