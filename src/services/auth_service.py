import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt

from src.database.models import User
from src.database.repository import FirebaseRepository
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self, repository: FirebaseRepository):
        self.repository = repository

    async def create_user(self, user_data: dict) -> User:
        """Create a new user with hashed password."""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data["email"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Hash password
            hashed_password = bcrypt.hashpw(
                user_data["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Create user object
            user = User(
                id=str(uuid.uuid4()),
                email=user_data["email"],
                hashed_password=hashed_password,
                role=user_data.get("role", "user"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Save to database
            await self.repository.create_user(user)
            return user

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user",
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user and return user object if valid."""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None

            if not bcrypt.checkpw(
                password.encode("utf-8"), user.hashed_password.encode("utf-8")
            ):
                return None

            return user

        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from database."""
        try:
            users_ref = self.repository.db.reference("users")
            users = users_ref.get()
            if not users:
                return None

            for user_id, user_data in users.items():
                if user_data.get("email") == email:
                    # Convert ISO format strings back to datetime objects
                    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                    user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])
                    return User(**user_data)
            return None

        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) 