"""
Security utilities for the FastAPI mini-blog.

Includes:
- Password hashing/verification (passlib: PBKDF2-SHA256).
- JWT creation/verification (python-jose).
- OAuth2 bearer token dependency for protected routes.
- Helpers: authenticate_user, get_current_user (DB-backed).
"""

# === Imports & Setup =========================================================
from passlib.context import CryptContext
import datetime
from jose import JWTError, jwt
from database import database, user_table
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer


# === Configuration (JWT & password hashing) ==================================
SECRET_KEY = "9b73f2a1bdd7ae163444473d29a6885ffa22ab26117068f72a5a56a74d12d1fc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# === Token & password helpers ================================================
def create_access_token(id_: str):
    """Create a signed JWT (HS256) for the given username (sub) with an expiry."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jwt_data = {"sub": id_, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using PBKDF2-SHA256 (passlib)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against a stored PBKDF2-SHA256 hash."""
    return pwd_context.verify(plain_password, hashed_password)


# === Auth helpers (DB lookups) ===============================================
async def get_user(username: str):
    """Fetch a user row by username; return the row or None if missing."""
    query = user_table.select().where(user_table.c.username == username)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(username: str, password: str):
    """Validate credentials; return user row if ok, else False."""
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# === Request dependency: current user ========================================
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode bearer JWT, load the user by `sub`, and return the DB row (401 on failure)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return user
