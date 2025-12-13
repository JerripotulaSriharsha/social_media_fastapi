from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate,RegisterIn,LoginIn
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from passlib.context import CryptContext
from sqlalchemy import select
from app.db import User
from app.auth import create_access_token, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan = lifespan)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# text_posts = {
#     1: {"title": "New Post", "content": "Cool test post"},
#     2: {"title": "Python Tip", "content": "Use list comprehensions for cleaner loops."},
#     3: {"title": "Daily Motivation", "content": "Consistency beats intensity every time."},
#     4: {"title": "Fun Fact", "content": "The first computer bug was an actual moth found in a Harvard Mark II."},
#     5: {"title": "Update", "content": "Just launched my new project! Excited to share more soon."},
#     6: {"title": "Tech Insight", "content": "Async IO in Python can massively speed up I/O-bound tasks."},
#     7: {"title": "Quote", "content": "\"Programs must be written for people to read, and only incidentally for machines to execute.\""},
#     8: {"title": "Weekend Plans", "content": "Might finally clean up my GitHub repos... or just play some Minecraft."},
#     9: {"title": "Question", "content": "What’s the most underrated Python library you’ve ever used?"},
#     10: {"title": "Mini Announcement", "content": "New video drops tomorrow—covering the weirdest Python features!!"},
# }

# @app.get("/posts")
# def get_all_posts(limit: int = None):
#     posts = list(text_posts.values())

#     if limit:
#         return posts[:limit]

#     return posts

# @app.get("/posts/{id}")
# def get_post(id: int):
#     if id not in text_posts:
#         raise HTTPException(status_code = 404,detail = "Page not found")
    
#     return text_posts.get(id)

# @app.post("/posts")
# def create_post(post: PostCreate):
#     new_post = {"title": post.title, "content": post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post


# @app.delete("/posts/{id}")
# def delete_post(id: int):
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     deleted_post = text_posts.pop(id)  # remove from dict and return it
#     return deleted_post
@app.post("/auth/register")
async def register(data: RegisterIn, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"id": str(user.id), "email": user.email}


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backle"]
            )
        )
        if upload_result.response_metadata.http_status_code == 200:
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name,
                 user_id= user.id
            )

            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    except Exception as e:
        raise HTTPException(status_code = 500,detail = str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
            }
        )

    return {"posts": posts_data}


@app.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    caption: str = Form(None),
    file: UploadFile = File(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    """
    Update a post's caption and/or media file.
    - post_id: UUID of the post to update
    - caption: New caption (optional)
    - file: New media file to replace existing one (optional)
    """
    temp_file_path = None
    try:
        # Convert post_id string to UUID
        post_uuid = uuid.UUID(post_id)

        # Find the post in database
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Update caption if provided
        if caption is not None:
            post.caption = caption

        # Update file if provided
        if file is not None:
            # Create temporary file from uploaded file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(file.filename)[1]
            ) as temp_file:
                temp_file_path = temp_file.name
                shutil.copyfileobj(file.file, temp_file)

            # Upload new file to ImageKit
            upload_result = imagekit.upload_file(
                file=open(temp_file_path, "rb"),
                file_name=file.filename,
                options=UploadFileRequestOptions(
                    use_unique_file_name=True,
                    tags=["backle"]
                )
            )

            if upload_result.response_metadata.http_status_code == 200:
                # Update post with new file information
                post.url = upload_result.url
                post.file_type = "video" if file.content_type.startswith("video/") else "image"
                post.file_name = upload_result.name
            else:
                raise HTTPException(status_code=500, detail="Failed to upload file to ImageKit")

        # Commit changes to database
        await session.commit()
        await session.refresh(post)

        # Return updated post
        return {
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "user_id": post.user_id
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if file:
            file.file.close()


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session),user: User = Depends(get_current_user)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))