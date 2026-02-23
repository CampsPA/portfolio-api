from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    email : EmailStr
    password : str
    first_name : str
    last_name : str



class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    first_name : str
    last_name : str


    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email : EmailStr | None = None
    first_name : str | None = None
    last_name : str | None = None


# This was added while creating the login endpoint
# Create a TokenData schema
class TokenData(BaseModel):
    email: str| None = None

class Token(BaseModel):
    access_token: str
    token_type: str






