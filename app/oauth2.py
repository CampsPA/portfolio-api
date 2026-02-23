import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
from .schemas.user import TokenData
from fastapi import status, HTTPException, Depends
from .models.user import User
from .database import get_db
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session 
from .config import settings
import logging


# Get a logger instance
logger = logging.getLogger("app.oauth2")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Create a function to generate tokens
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Log sucessful token creation
    logger.info("Token successfully generated.")

    return encoded_jwt



# Create a function to verify/decode the tokens
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        logger.info("Token decoded and validated.") # Happy path log
    except InvalidTokenError:
        logger.warning("Token could not be  validated.") # Invalid or expired token
        raise credentials_exception

    
    return token_data


# Create a get_current_user function
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception) # this was created above
    user = db.query(User).filter(User.email == token_data.email).first()
    logger.info("User successfully validated.")

    if user is None:
        logger.warning("Authenticated token references a user that does not exist in the database.")
        raise credentials_exception
    return user
