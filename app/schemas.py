from pydantic import BaseModel
import uuid

class PostCreate(BaseModel):
    title: str
    content: str

class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str