"""
Feature
- Authentication (email, username, password)
- User preference
- Profile Information
- Account status management
"""

from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, String, JSON
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
    EDUCATOR = "educator" # เผื่อรันในมหาลัยได้

class AIPersonalityLevel(int, enum.Enum):
    "ระดับความสนิทกับ AI"

    POLITE = 1
    FRIENDLY = 2
    INTIMATE = 3

class UserStatus(str, enum.Enum):
    "สถานะบัญชีผู้ใช้"

    ACTIVE = "active" # ใช่งานปกติ
    INACTIVE = "inactive" # ยังไม่ยืนยัน email
    SUSPENDED = "suspended" # ถูกระงับ
    BANNED = "banned" # ถูกแบน

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

    pasword_hash: str = Field(
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

    date_of_birth: Optional[date] = Field(
        default = None,
        max_length = 100,
        description = "วันเกิด"
    )

    occupation: Optional[str] = Field(
        default = None,
        max_length = 100,
        description = "อาชีพ"
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

    #=== AI Preference ======
    ai_personality_level: AIPersonalityLevel = Field(
        default = AIPersonalityLevel.POLITE,
        description = "ระดับความสนิทกับ AI"
    )

    ai_daily_limit: int = Field(
        default = 0,
        description = "จำนวนครั้งที่ใช้ AI ได้ต่อวัน "
    )

    ai_used_today: int = Field(
        default = 0,
        description = "จำนวนครั้งที่ใช้ AI ไปวันนี้"
    )

    # ===== User Settings (JSON) =======

    settings: Dict[str, Any] = Field(
        default_factory = dict,
        sa_column = Column(JSON),
        description = "การตั้งค่าของผู้ใช้"
    )

    # ======= financial preference =======
    preferred_currency: str = Field(
        default = "THB",
        max_length = 3,
        description = "สกุลเงินที่ใช้"
    )

    monthly_income: Optional[float] = Field(
        default = None,
        description = "รายได้ต่อเดือน"
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
    
    @property
    def can_use_ai(self) -> bool:
        if self.is_premium:
            return True
        return self.ai_used_today < self.ai_daily_limit
    
    @property
    def age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
# ====== User Schema สำหรับ API

class UserRead(SQLModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    date_of_birth: Optional[date]
    role: UserRole
    status: UserStatus
    is_verified: bool
    ai_personality_level: AIPersonalityLevel
    preferred_currency: str
    created_at: str

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
    
class UserCreate(SQLModel):
    email: str = Field(min_length = 5, max_length = 255)
    username: str = Field(min_length = 3, max_length = 50)
    password: str = Field(min_length = 8, max_length = 100)
    first_name: Optional[str] = Field(default = None, max_length = 100)
    last_name: Optional[str] = Field(default = None, max_length = 100)
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(default = None, max_length = 100)

class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(default=None, max_length=100)
    ai_personality_level: Optional[AIPersonalityLevel] = None
    preferred_currency: Optional[str] = Field(default=None, max_length=3)
    monthly_income: Optional[float] = None

class UserSetting(SQLModel):
    notifications_enabled: bool = True
    email_notifications: bool = True
    dark_mode: bool = False
    language: str = "th"
    timezone: str = "Asia/Bangkok"
    auto_categorize: bool = True
    ai_tips_frequency: str = "daily" 

# ==== Helper Function ==========
def create_default_settings() -> Dict[str, Any]:
    "สร้าง Default setting ให้ User ใหม่"
    
    return {
        "notifications_enabled": True,
        "email_notifications": True,
        "dark_mode": False,
        "language": "th",
        "timezone": "Asia/Bangkok",
        "auto_catagorize": True,
        "ai_tips_frequency": "daily"
    }

def upgrade_to_premium(user: User) -> User:
    user.role = UserRole.PREMIUM
    user.ai_daily_limit = 500
    user.updated_at = utc_now()

def reset_daily_ai_usage(user: User) -> User:
    user.ai_used_today = 0
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
        settings=create_default_settings()
    )
    
    print(f"User ID: {new_user.id}")
    print(f"Full name: {new_user.full_name}")
    print(f"Is premium: {new_user.is_premium}")
    print(f"Can use AI: {new_user.can_use_ai}")
    print(f"Settings: {new_user.settings}")
    
    # ทดสอบ upgrade to premium
    print("\n=== Testing Premium Upgrade ===")
    upgrade_to_premium(new_user)
    print(f"Role after upgrade: {new_user.role}")
    print(f"AI daily limit: {new_user.ai_daily_limit}")
    
    print("\n✅ User Model ทำงานปกติ!")