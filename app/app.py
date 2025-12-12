from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate #, PostResponse, UserRead, UserCreate, UserUpdate
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
# from app.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan = lifespan)

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

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session)
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
                file_name=upload_result.name
            )

            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    except Exception as e:
        raise HTTPException(statuscode = 500,denial = str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
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
                "created_at": post.created_at.isoformat()
            }
        )

    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
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