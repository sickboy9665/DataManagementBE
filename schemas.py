from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserInDB(UserCreate):
    id: int
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True
