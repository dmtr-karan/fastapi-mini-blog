"""
FastAPI Mini-Blog API

Implements:
- Registration and OAuth2 login (JWT)
- Auth-protected write endpoints for posts and comments
- Nested read: GET /posts/{id} returns a post with its comments
- Dev utilities: /health and guarded /_dev/reset

Conventions:
- Response models hide internal DB fields
- Small, readable handlers; no framework-specific magic
"""

# === Imports & Setup =========================================================
from database import database, posts, user_table, comments_table
from fastapi import FastAPI, HTTPException, status, Depends, Query, Response
from models.post import (UserPost, UserPostIn, CommentOut,
                         CommentIn, UserPostWithComments)
from models.user import UserIn, User
from security import (get_password_hash, create_access_token,
                      authenticate_user, get_current_user)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

# === Application =============================================================
app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")


# === Setup Events =============================================================
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# === Color Theme: Swagger UI Docs ===========================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=(app.openapi_url or "/openapi.json"),
        title="FastAPI Mini-Blog — Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        # Use our combined CSS (imports default + overrides)
        swagger_css_url="/static/swagger-dark.css?v=1",
    )

# === Dev Utilities: health + reset (guarded) ================================
ALLOWED_MAINTAINERS = {"dim"}  # Allow only specific users to hit dev-only endpoints


def verify_maintainer(user: User = Depends(get_current_user)) -> User:
    if user.username not in ALLOWED_MAINTAINERS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@app.get("/health")
async def health():
    """
    Lightweight liveness probe.
    """
    return {"status": "ok"}


@app.post("/_dev/reset", status_code=204)
async def dev_reset_db(_: User = Depends(verify_maintainer)):
    """
    Dev-only maintenance: clear comments then posts. Returns 204 No Content.
    """
    await database.execute(comments_table.delete())
    await database.execute(posts.delete())
    return Response(status_code=204)


# === Auth ===================================================================
@app.post("/register", status_code=201)
async def register(user: UserIn):
    """
    Register a user and return an access token.
    """
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(username=user.username, password=hashed_password)
    await database.execute(query)
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 password flow: return an access token for Swagger / 'Authorize'.
    """
    username = form_data.username
    password = form_data.password

    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# === Write endpoints (auth required) ========================================
@app.post("/post", status_code=201, response_model=UserPost)
async def create_post(
    post: UserPostIn, current_user: User = Depends(get_current_user)
):
    """
    Create a new post for the authenticated user. Returns the created post.
    """
    data = {**post.dict(), "user_id": current_user.id}
    query = posts.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@app.post("/comment", status_code=201, response_model=CommentOut)
async def create_comment(
    comment: CommentIn, current_user: User = Depends(get_current_user)
):
    """
    Add a comment to an existing post (404 if post_id does not exist).
    Returns the created comment (minimal response model).
    """
    # --- FK validation: ensure post exists ---
    query_post = posts.select().where(posts.c.id == comment.post_id)
    post = await database.fetch_one(query_post)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # --- proceed normally ---
    data = {**comment.dict(), "user_id": current_user.id}
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


# === Read endpoints ==========================================================
@app.get("/post/{post_id}/comments", response_model=list[CommentOut])
async def get_comments_on_post(post_id: int):
    """
    List comments for a specific post with optional pagination.
    """
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    return await database.fetch_all(query)


@app.get("/posts/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    """
    Retrieve a single post and its comments (404 if not found).
    """
    query = posts.select().where(posts.c.id == post_id)
    post = await database.fetch_one(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    comments = await database.fetch_all(query)
    return {**dict(post), "comments": comments}


@app.get("/posts", response_model=list[UserPost])
async def get_all_posts(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """
    List posts with optional pagination (limit/skip).
    """
    query = posts.select().order_by(posts.c.id.desc()).limit(limit).offset(skip)
    rows = await database.fetch_all(query)
    return rows
# === End of file =============================================================
