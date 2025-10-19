from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Form,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_confirm_email, send_reset_email
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Annotated


router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="templates")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_confirm_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not confirmed"
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed successfully"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Email already confirmed"}
    if user:
        background_tasks.add_task(
            send_confirm_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email"}


@router.post("/request_reset_password")
async def request_reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is not None:
        background_tasks.add_task(
            send_reset_email, user.email, user.username, request.base_url
        )

    return {"message": "Check your email"}


@router.get(
    "/password_reset/{token}",
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def get_password_reset_page(request: Request):
    return templates.TemplateResponse("reset_password_form.html", {"request": request})


@router.post(
    "/password_reset/{token}",
    description="No more than 10 requests per minute",
)
async def reset_password(
    token: str,
    new_password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    if new_password == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No password provided"
        )

    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is no longer exists"
        )

    hashed_password = Hash().get_password_hash(new_password)
    await user_service.update_user_password(email, hashed_password)

    return {"message": "Password updated successfully"}
