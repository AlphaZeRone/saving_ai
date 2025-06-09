from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
import uuid

class TimestampMixin(SQLModel):
    """ 
    Mixin สำหรับ timestamp fields
    เพิ่มเวลา create, update สำหรับทุก Model
    """

    created_at: datetime = Field(
        default = None,
        nullable = True,
        description = "เวลาที่สร้าง"
    )

    updated_at: datetime = Field(
        default = None,
        nullable = True,
        description = "แก้ไขล่าสุด"
    )

class BaseModel(TimestampMixin):
    """
    BaseModel ของ table ทั้งหมด สำหรับ Feature ที่มีทุก Model

    Feature:
    - UUID primary key
    - Timestamp tracking
    - prepare for soft delete
    """

    id: uuid.UUID = Field(
        default_factory = uuid.uuid4,
        primary_key = True,
        description = "Primary key UUID"
    )

    is_deleted: bool = Field(
        default = False,
        nullable = False, 
        description = "สำหรับการทำ Soft delete"
    )

    deleted_at: Optional[datetime] = Field(
        default = None,
        nullable = True,
        description = "เวลาที่ทำการลบ (soft delete)"
    )

class TimeSeriesBaseModel(TimestampMixin):
    """
    BaseModel สำหรับ hyper tables ใน timescaledb ที่เป็น time-series data เช่น
    transaction, chat_history 
    - ไม่ใช้ UUID เพราะ TimeScaleDB ทำงานได้ดีกับ int
    """

    id: Optional[int] = Field(
        default = None,
        primary_key = True,
        description = "Primary key (Auto increments integer)"
    )

# ========== Helper Fuction =================

def generate_uuid() -> str:
    "สร้าง UUID string สำหรับใช้ในกรณีพิเศษ"
    return str(uuid.uuid4())

def utc_now() -> datetime:
    "รับเวลาตาม timezone"
    return datetime.now(timezone.utc)

# ========= Model Utilities ===========

class ModelUtils:
    "Utility functions"

    @staticmethod
    def soft_delete(model_instance: BaseModel) -> BaseModel:
        model_instance.is_deleted = True
        model_instance.deleted_at = utc_now()
        model_instance.updated_at = utc_now()
        return model_instance
    
    @staticmethod
    def restore_deleted(model_instance: BaseModel) -> BaseModel:
        model_instance.is_deleted = False
        model_instance.deleted_at = None
        model_instance.updated_at = utc_now()

    @staticmethod
    def update_timestamp(model_instance: BaseModel) -> BaseModel:
        model_instance.updated_at = utc_now()

# ========= Example =============
if __name__ == "__main__":
    print("=== Testing BaseModel ===")

    class TestModel(BaseModel, table = True):
        __tablename__ = "test_table"

        name: str = Field(description = "Testing")

    test_instance = TestModel(name = "Test Record")

    print(f"ID: {test_instance.id}")
    print(f"Created at: {test_instance.created_at}")
    print(f"Is deleted: {test_instance.is_deleted}")

    # Soft delete Testing
    print("=== Soft Delete Testing ===")
    ModelUtils.soft_delete(test_instance)
    print(f"Is Deleted: {test_instance.is_deleted}")
    print(f"Deleted at: {test_instance.deleted_at}")

    # Restore Testing
    print("=== Restore Testing ===")
    ModelUtils.restore_deleted(test_instance)
    print(f"Is Deleted: {test_instance.is_deleted}")
    print(f"Deleted at: {test_instance.deleted_at}")

    print("\n✅ BaseModel ทำงานปกติ")