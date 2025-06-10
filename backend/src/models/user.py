"""
Feature
- Authentication (email, username, password)
- User preference
- Profile Information
- Account status management
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date
import enum

try:
    from .base import BaseModel, utc_now
except ImportError:
    from base import BaseModel, utc_now

# ===== Enums สำหรับ User =====

class UserRole(str, enum.Enum):
    "บทบาทของ User"

    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin" 

class UserStatus(str, enum.Enum):
    "สถานะบัญชีผู้ใช้"

    ACTIVE = "active" # ใช่งานปกติ
    INACTIVE = "inactive" # ยังไม่ยืนยัน email

# ====== UserModel =======

class User(BaseModel, table = True):
    """
    UserModel

    Feature
    - ใช้ BaseModel
    - Authentications Field
    - Profile Information
    - AI preference
    - User settings
    """

    __tablename__ = "users"

    #===== Authentications Fields ====
    email: str = Field(
        unique = True,
        index = True,
        max_length = 255,
        description = "อีเมลผู้ใช้ (unique)"
    )

    username: str = Field(
        unique = True,
        index = True,
        max_length = 50,
        description = "ชื่อผู้ใช้ (unique)"
    )

    password_hash: str = Field(
        max_length = 255,
        description = "รหัสผ่านที่เข้ารหัสแล้ว"
    )

    # ======= Profile Information ========

    first_name: Optional[str] = Field(
        default = None,
        max_length = 100,
        description = "ชื่อจริง"
    )

    last_name: Optional[str] = Field(
        default = None,
        max_length = 100,
        description = "นามสกุล"
    )

    display_name: Optional[str] = Field(
        default = None,
        max_length = 100,
        description = "ชื่อที่แสดง (ไม่มีใช้ username)"
    )

    # ===== Account Status =======
    role: UserRole = Field(
        default = UserRole.FREE,
        description = "บทบาทผู้ใช้"
    )

    status: UserStatus = Field(
        default = UserStatus.INACTIVE,
        description = "สถานะผู้ใช้"
    )

    is_verified: bool = Field(
        default = False,
        description = "ยืนยันอีเมล"
    )

    last_login_at: Optional[date] = Field(
        default = None,
        description = "เข้าสู่ระบบครั้งล่าสุด"
    )

    # ==== Compute Properties ======
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username
    
    @property
    def is_premium(self) -> bool:
        return self.role in [UserRole.PREMIUM, UserRole.ADMIN]
    
    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.is_active
    
# ====== User Schema สำหรับ API

class UserRead(SQLModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    role: UserRole
    status: UserStatus
    is_verified: bool
    created_at: str

class UserCreate(SQLModel):
    email: str = Field(min_length = 5, max_length = 255)
    username: str = Field(min_length = 3, max_length = 50)
    password: str = Field(min_length = 8, max_length = 100)
    first_name: Optional[str] = Field(default = None, max_length = 100)
    last_name: Optional[str] = Field(default = None, max_length = 100)

class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)

# ==== Helper Function ==========

def active_user(user: User) -> User:
    "เปิดใช้งาน User"
    user.status = UserStatus.ACTIVE
    user.is_verified = True
    user.updated_at = utc_now()
    return user

# ========= Example =================
if __name__ == "__main__":
    """ทดสอบ User Model"""
    
    print("=== Testing User Model ===")
    
    # สร้าง user ใหม่
    new_user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password_here",
        first_name="Test",
        last_name="User",
    )
    
    print(f"User ID: {new_user.id}")
    print(f"Full name: {new_user.full_name}")
    print(f"Is premium: {new_user.is_premium}")
    print(f"Is active: {new_user.is_active}")
    print(f"Status: {new_user.status}")
    
    # ทดสอบ activate user
    print("\n=== Testing User Activation ===")
    active_user(new_user)
    print(f"Status after activation: {new_user.status}")
    print(f"Is verified: {new_user.is_verified}")
    
    print("\n✅ User Model ทำงานปกติ!")