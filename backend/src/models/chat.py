from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime
import enum
import uuid

try:
    from .base import BaseModel, utc_now
except ImportError:
    from base import BaseModel, utc_now

# ====== Enums สำหรับ chat =======
class MessageSender(str, enum.Enum):
    "ใครเป็นคนส่ง chat"

    AI = "ai"
    USER = "user"

class ConversationStatus(str, enum.Enum):
    "สถานะของบทสนทนา"

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

# ======= Chat models ======

" แบ่ง Conversation Model กับ Message Model "

# ===== Conversaiton Models
class Conversation(BaseModel, table = True):
    __tablename__ = "conversations"

    # ===== Conversation Informations ========
    user_id: uuid.UUID = Field(
        foreign_key = "users.id",
        description = "เจ้าของบทสนทนา"
    )

    topic: str = Field(
        max_length = 40,
        description = "หัวข้อการสนทนา"
    )

    total_message: int = Field(
        default = 0,
        description = "จำนวนข้อความทั้งหมด"
    )

    # ===== Conversations Status ====== 
    status: ConversationStatus = Field(
        default = ConversationStatus.ACTIVE,
        description = "สถานะของบทสนทนา"
    )

# ====== Message Models ======
class Message(BaseModel, table = True):
    __tablename__ = "messages"

    # ===== Message Informations ======
    conversation_id: uuid.UUID = Field(
        foreign_key = "conversations.id",
        description = "บทสนทนาที่อยู่"
    )

    content: str = Field(
        description = "เนื้อหา"
    )

    sender_type: MessageSender = Field(
        description = " ผู้ส่ง"
    )

    message_index: int = Field(
        default = 1,
        description = "ข้อความที่เท่าไหร่ใน conversation"
    )

    # ===== AI Specific Field =======
    token_used: int = Field(
        default = 0,
        description = "จำนวน Token ที่ AI ใช้ไป"
    )

    response_time_ms: int = Field(
        default = 0,
        description = "ระยะเวลาที่ใช้ในการหาคำตอบ (ms)"
    )

    ai_model: Optional[str] = Field(
        default = None,
        description = "โมเดล AI ที่ใช้งาน"
    )

# ========== Message Rating Model =======
class MessageRating(BaseModel, table = True):
    __tablename__ = "message_ratings"

    # ===== Rating Information ========
    message_id: uuid.UUID = Field(
        foreign_key = "messages.id",
        description = "ข้อความที่ได้รับ rating"
    )

    user_rating: Optional[int] = Field(
        default = None,
        description = "คะแนน"
    )

# ====== Helper Function =========
def generate_topic_from_message(message: str, max_chars: int = 40) -> str:
    if len(message) <= max_chars:
        return message
    else :
        return message[:max_chars] + "..."
    
# ====== Chat Schema ============

# Conversation Schema
class ConversationRead(SQLModel):
    id: str
    user_id: str
    topic: str
    total_message: int
    status: ConversationStatus
    created_at: str
    updated_at: Optional[str]

class ConversationUpdate(SQLModel):
    topic: Optional[str]
    status: Optional[ConversationStatus]
    updated_at: Optional[str]

# Message Schema
class MessageRead(SQLModel):
    id: str
    conversation_id: str
    content: str
    sender_type: MessageSender
    message_index: int
    created_at: str
    updated_at: Optional[str]

    # ===== AI_Specific Field =========
    token_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    ai_model: Optional[str] = None

class MessageCreate(SQLModel):
    content: str

class MessageUpdate(SQLModel):
    content: Optional[str]
    updated_at: Optional[str]

# Rating Schema
class RatingRead(SQLModel):
    id: str
    message_id: str
    user_rating: Optional[int]
    created_at: str
    updated_at: Optional[str]

class RatingCreate(SQLModel):
    user_rating: int

# ====== Pagination ========
class PaginationInfo(SQLModel):
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class ConversationPaginatedResponse(SQLModel):
    data: List[ConversationRead]
    pagination: PaginationInfo

class MessagePaginated(SQLModel):
    data: List[MessageRead]
    pagination: PaginationInfo

# ===== Response ==========
class ChatResponse(SQLModel):
    user_message: MessageRead
    ai_message: MessageRead
    conversation: ConversationRead
    recent_messages: List[MessageRead]

