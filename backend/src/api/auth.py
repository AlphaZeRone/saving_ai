"""
Authentication API

Session-Based Authentication 
- Register
- login
- logout
- User Profile
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select
from typing import Optional

from core.database import get_session
from core.security import hash_password, verify_password, generate_session_token
from models.user import User, UserCreate, UserRead, UserStatus, active_user

router = APIRouter()

# ===== Session Storage เก็บใน memory =========

active_sessions = {}

# ======= Helper Functtion =========

def get_current_user(request: Request, session: Session = Depends(get_session)) -> Optional[User]:
    
    # ดึง Session Token 
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    # ค้นหา user_id
    user_id = active_sessions.get(session_token)
    if not user_id:
        return None
    
    # ดึงข้อมูล user จาก database
    user = session.get(User, user_id)
    if not user or user.is_deleted:
        return None
    
    return user

def require_auth(request: Request, session: Session = Depends(get_session)) -> User:
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "กรุณาเข้าสู่ระบบก่อน"
        )
    
    return user

# ======= API Endpoint ==========

@router.post("/register", response_model = UserRead, status_code = status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    # ตรวจสอบ email ซ้ำ
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "อีเมลนี้ถูกใช้งานแล้ว"
        )
    
    # ตรวจสอบ Username ซ้ำ
    exsiting_username = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if exsiting_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "ชื่อผู้ใช้นี้ถูกใช้งานแล้ว"
        )
    
    # hash password
    password_hash = hash_password(user_data.password)

    # Create user object
    new_user = User(
        email = user_data.email,
        username = user_data.username,
        password_hash = password_hash,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        status = UserStatus.ACTIVE,
        is_verified = True
    )

    # Save to DB
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # แปลง User object เป็น UserRead response
    user_response = UserRead(
        id = str(new_user.id),
        email = new_user.email,
        username = new_user.username,
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        display_name = new_user.display_name,
        role = new_user.role,
        status = new_user.status,
        is_verified = new_user.is_verified,
        created_at = new_user.created_at.isoformat()
    )

    return user_response

# ====== Login Schema ==========

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    user: UserRead
    message: str

# ====== Login Endpoint ======

@router.post("/login", response_model = LoginResponse)
async def login_user(
    login_data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    
    # หา User จาก Email
    user = session.exec(
        select(User).where(User.email == login_data.email)
    ).first()

    # ตรวจสอบว่า User และ Password ถูกต้อง
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        )
    
    # ตรวจสอบสถานะ user
    if user.is_deleted or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "บัญชีนี้ไม่สามารถใช้งานได้"
        )
    
    # สร้าง session token
    session_token = generate_session_token()

    # เก็บ session ใน memory
    active_sessions[session_token] = str(user.id)

    # ตั้งค่า cookies ใน response
    response.set_cookie(
        key = "session_token",
        value = session_token,
        max_age = 7 * 24 * 60 * 60, # 7 วันแบบวินาที
        httponly = True,
        secure = False,
        samesite = "lax"
    )

    # update last_login_at
    from datetime import date
    user.last_login_at = date.today()
    session.add(user)
    session.commit()

    # create response
    user_response = UserRead(
        id = str(user.id),
        email = user.email,
        username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        display_name = user.display_name,
        role = user.role,
        status = user.status,
        is_verified = user.is_verified,
        created_at = user.created_at.isoformat()
    )

    return LoginResponse(
        user = user_response,
        message = f"ยินดีต้อนรับ {user.display_name}"
    )

# ======== Current User Endpoint =========

@router.get("/me", response_model = UserRead)
async def get_current_user_info(
    request: Request,
    session: Session = Depends(get_session)
):
    
    # ใช้ helper function ช่วยตรวจสอบ authentication
    user = require_auth(request, session)

    # แปลง object เป็น UserRead Response
    user_response = UserRead(
        id = str(user.id),
        email = user.email,
        username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        display_name = user.display_name,
        role = user.role,
        status = user.status,
        is_verified = user.is_verified,
        created_at = user.created_at.isoformat()
    )

    return user_response

# ====== Logout Endpoint ========

@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response
):
    
    # ดึง session token จาก cookie
    session_token = request.cookies.get("session_token")

    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    # ลบ cookies
    response.delete_cookie(
        key = "session_token",
        httponly = True,
        secure = False,
        samesite = "lax"
    )

    return {"message": "ออกจากระบบเรียบร้อย"}

# ======= Check Login Status =======
@router.get("/status")
async def check_login_status(
    request: Request,
    session: Session = Depends(get_session)
):
    user = get_current_user(request, session)

    if user:
        return {
            "logged_in": True,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "full_name": user.full_name
            }
        }
    
    else:
        return {
            "logged_in": False,
            "user": None
        }