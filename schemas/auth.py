from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserCreate(BaseModel):
    # Schema for user registration
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    # Schema for user login
    email: EmailStr
    password: str


class Token(BaseModel):
    # Schema for JWT token response
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    # Schema for user response
    id: UUID
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
