from pydantic import BaseModel
import uuid

class PostCreate(BaseModel):
    title: str
    content: str