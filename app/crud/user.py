"""Create two functions:
1- create_user
2- get_user_by_email
"""

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session
from ..utils import  hash_password
import logging


# Get a logger instance
logger = logging.getLogger("app.crud.user")


def create_user(db : Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    new_user = User(email= user.email, hashed_password = hashed_password,first_name=user.first_name,
    last_name=user.last_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User with id {new_user.id} successfully created.")
    return new_user
    

def get_user_by_email(db : Session, email : str):
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        logger.info(f"No user found.")
        return None
    else:
        logger.info("User successfully retrieved.")
    return user


def update_user(db : Session, email : str, user_data : UserUpdate):
    user = get_user_by_email(db, email)


    if user_data.email is not None:
        user.email = user_data.email

    if user_data.first_name is not None:
        user.first_name  = user_data.first_name

    if user_data.last_name is not None:
        user.last_name  = user_data.last_name

    db.commit()
    db.refresh(user)
    logger.info("User successfully updated.")
    return user

    

