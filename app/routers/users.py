from fastapi import APIRouter, Depends
from ..schemas.user import  UserResponse, UserUpdate
from ..oauth2 import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..crud.user import update_user
import logging


# Get a logger instance
logger = logging.getLogger("app.routers.users")


router = APIRouter(tags=['Users'])

# Create a get /me endpoint for the authenticated user.
# Receive a response model in the decorator
# Receive the current model we are woring with (current_user) and set Depends to the function 
# that gets the current user
# Return the current user
@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    logger.info(f"Current user with id {current_user.id} successfully retrieved.")
    return current_user


# Update user
@router.put("/me", response_model=UserResponse)
def update_user_profile(user_data : UserUpdate, db: Session =Depends(get_db), current_user = Depends(get_current_user)):
    updated_user = update_user(db, current_user.email, user_data)
    logger.info(f"User profile successfully updated for user id {current_user.id}.")
    return updated_user


