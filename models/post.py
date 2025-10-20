"""
Pydantic models for posts and comments.

Defines:
- Input and output schemas for posts and comments.
- Variants that hide internal fields (e.g., user_id) from API responses.
- Combined model (UserPostWithComments) for nested post detail views.
"""

# === Imports & Setup =========================================================
from pydantic import BaseModel


# === Post models =============================================================
class UserPostIn(BaseModel):
    """Incoming post payload from client (no user_id)."""
    body: str


class UserPost(UserPostIn):
    """Full post representation including author linkage."""
    id: int


# === Comment models ==========================================================
class CommentIn(BaseModel):
    """Incoming comment payload with post_id reference."""
    body: str
    post_id: int


class Comment(CommentIn):
    """Full comment record including user and post IDs."""
    id: int
    user_id: int


class CommentOut(BaseModel):
    """Response model for created or fetched comments (user_id hidden)."""
    body: str
    post_id: int
    id: int


# === Combined models =========================================================
class UserPostWithComments(UserPost):
    """Nested model combining a post and its list of comments."""
    comments: list[CommentOut]

