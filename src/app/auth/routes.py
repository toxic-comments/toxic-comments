from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from app.dependencies import get_session
from app.database import User
from .security import hash_password, verify_password, create_access_token

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth")


class RegisterRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(min_length=3, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session),):
    if session.query(User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="user",
    )
    session.add(user)
    session.commit()

    #return {"status": "ok"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.query(User).filter_by(username=form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.role)
    return Token(access_token=token, token_type="bearer")