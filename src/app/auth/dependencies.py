from fastapi.params import Depends
from fastapi import HTTPException, status, Header
from jose import JWTError
from app.auth.security import decode_access_token
from app.database import User
from app.dependencies import get_session
from fastapi.security import OAuth2PasswordBearer

from bot.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session = Depends(get_session),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user




async def get_current_bot_user(
    x_api_key: str = Header(..., alias="X-API-Key"),
    x_telegram_id: int = Header(..., alias="X-Telegram-Id"),
    session = Depends(get_session),
) -> User:
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    user = session.query(User).filter(User.id == x_telegram_id).first()
    
    if not user:
        user = User(
            id=x_telegram_id, 
            username="tg_user",
            password_hash="TG_PASSWORD_klsjhdflkasjhdflakjsdf;asdfsdsssssssl",
            role="user"
            )
        session.add(user)
        session.commit()
        session.refresh(user)

    return user