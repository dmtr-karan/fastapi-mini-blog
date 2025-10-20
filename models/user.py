"""
Pydantic models for users.

- User: public/user-facing fields.
- UserIn: extends User with plaintext password for registration input.
"""

# === Imports & Setup =========================================================
from pydantic import BaseModel


class User(BaseModel):
    """Public user representation used in responses and dependencies."""
    id: int | None = None
    username: str


class UserIn(User):
    """Incoming registration payload; includes plaintext password."""
    password: str
