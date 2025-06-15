from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import date
import enum
import uuid

try:
    from .base import BaseModel, utc_now
except ImportError:
    from base import BaseModel, utc_now

# ======= Enum สำหรับ transaction ==========
class TransactionType(str, enum.Enum):
    "ประเภทของธุรกรรม"

    INCOME = "รายรับ"
    EXPENSE = "รายจ่าย"

# ======= Transaction Model ==========
class Transaction(BaseModel, table = True):
    __tablename__ = "transactions"

    #====== Transaction Information ========
    user_id: uuid.UUID = Field(
        foreign_key = "users.id",
        description = "เจ้าของรายการ"
    )

    amount: float = Field(
        description = "จำนวนเงิน"
    )

    type: TransactionType = Field(
        default = None,
        description = "ประเภทของธุรกรรม"
    )

    category: str = Field(
        max_length = 255,
        description = "หมวดหมู่ของธุรกรรม"
    )

    description: str = Field(
        max_length = 255,
        description = "คำอธิบายรายการธุรกรรม"
    )

    note: Optional[str] = Field(
        default = None,
        max_length = 255,
        description = "จดโน๊ด"
    )

    transaction_date: date = Field(
        default = None,
        description = "วันที่ทำรายการ"
    )

    is_ai_categorize: bool = Field(
        default = False,
        description = "จัดหมวดหมู่ด้วย AI หรือยัง"
    )

# ====== Transaction Schema สำหรับ API
class TransactionRead(SQLModel):
    id: str
    user_id: str
    amount: float
    type: TransactionType
    category: str
    description: str
    note: Optional[str]
    transaction_date: date
    is_ai_categorize: bool
    created_at: str
    updated_at: Optional[str]

class TransactionCreate(SQLModel):
    amount: float
    type: TransactionType
    category: str
    description: str
    note: Optional[str]
    transaction_date: date

class TransactionUpdate(SQLModel):
    amount: Optional[float]
    type: Optional[TransactionType]
    category: Optional[str]
    description: Optional[str]
    note: Optional[str]
    transaction_date: Optional[date]

# ======== Pagination Response ================
class PaginationInfo(SQLModel):
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class TransactionPaginatedResponse(SQLModel):
    data: List[TransactionRead]
    pagination: PaginationInfo
