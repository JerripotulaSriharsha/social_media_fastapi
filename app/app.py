from fastapi import FastAPI,HTTPException
from app.schemas import PostCreate
app = FastAPI()
text_posts = {
    1: {"title": "New Post", "content": "Cool test post"},
    2: {"title": "Python Tip", "content": "Use list comprehensions for cleaner loops."},
    3: {"title": "Daily Motivation", "content": "Consistency beats intensity every time."},
    4: {"title": "Fun Fact", "content": "The first computer bug was an actual moth found in a Harvard Mark II."},
    5: {"title": "Update", "content": "Just launched my new project! Excited to share more soon."},
    6: {"title": "Tech Insight", "content": "Async IO in Python can massively speed up I/O-bound tasks."},
    7: {"title": "Quote", "content": "\"Programs must be written for people to read, and only incidentally for machines to execute.\""},
    8: {"title": "Weekend Plans", "content": "Might finally clean up my GitHub repos... or just play some Minecraft."},
    9: {"title": "Question", "content": "What’s the most underrated Python library you’ve ever used?"},
    10: {"title": "Mini Announcement", "content": "New video drops tomorrow—covering the weirdest Python features!!"},
}

@app.get("/posts")
def get_all_posts(limit: int = None):
    posts = list(text_posts.values())

    if limit:
        return posts[:limit]

    return posts

@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code = 404,detail = "Page not found")
    
    return text_posts.get(id)

@app.post("/posts")
def create_post(post: PostCreate):
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post


@app.delete("/posts/{id}")
def delete_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    deleted_post = text_posts.pop(id)  # remove from dict and return it
    return deleted_post
