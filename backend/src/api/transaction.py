from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select, func
from typing import Optional, List

from core.database import get_session
from models.transaction import Transaction, TransactionType, TransactionCreate, TransactionRead, TransactionUpdate, PaginationInfo, TransactionPaginatedResponse
from models.user import User
from api.auth import require_auth
from models.base import utc_now
from core.ai_service import MoneyAI

router = APIRouter()

# ===== API Endpoint ============

# Create Transaction
@router.post("/create", response_model = TransactionRead, status_code = status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    # Create Transaction objects
    new_transaction = Transaction(
        user_id = current_user.id,
        amount = transaction_data.amount,
        type = transaction_data.type,
        category = transaction_data.category,
        description = transaction_data.description,
        note = transaction_data.note,
        transaction_date = transaction_data.transaction_date,
    )

    # Save to DB
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    # แปลง object เป็น TransactionRead Response
    transaction_response = TransactionRead(
        id = str(new_transaction.id),
        user_id = str(new_transaction.user_id),
        amount = new_transaction.amount,
        type = new_transaction.type,
        category = new_transaction.category,
        note = new_transaction.note,
        description = new_transaction.description,
        transaction_date = new_transaction.transaction_date,
        is_ai_categorize = new_transaction.is_ai_categorize,
        created_at = new_transaction.created_at.isoformat(),
        updated_at = new_transaction.updated_at.isoformat() if new_transaction.updated_at else None
    )

    return transaction_response

# Update user transaction
@router.put("/update/{transaction_id}", response_model = TransactionRead)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "ไม่พบธุรกรรม"
        )
    
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "ไม่พบธุรกรรม"
        )
    
    if update_data.amount is not None:
        transaction.amount = update_data.amount
    if update_data.type is not None:
        transaction.type = update_data.type
    if update_data.description is not None:
        transaction.description = update_data.description
    if update_data.category is not None:
        transaction.category = update_data.category
    if update_data.note is not None:
        transaction.note = update_data.note
    if update_data.transaction_date is not None:
        transaction.transaction_date = update_data.transaction_date
    transaction.updated_at = utc_now()

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    transaction_response = TransactionRead(
        id = str(transaction.id),
        user_id = str(transaction.user_id),
        amount = transaction.amount,
        type = transaction.type,
        category = transaction.category,
        description = transaction.description,
        note = transaction.note,
        transaction_date = transaction.transaction_date,
        is_ai_categorize = transaction.is_ai_categorize,
        created_at = transaction.created_at.isoformat(),
        updated_at = transaction.updated_at.isoformat() if transaction.updated_at else None
    )

    return transaction_response

# Delete User transactions
@router.delete("/delete/{transaction_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "ไม่พบธุรกรรม"
        )
    
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "ไม่พบธุรกรรม"
        )
    
    session.delete(transaction)
    session.commit()

# Categorize user transaction
@router.post("/categorize/{transaction_id}")
async def categorize_transaction(
    transaction_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "ไม่พบธุรกรรม"
        )
    
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "ไม่พบธุรกรรม"
        )
    
    try:
        ai = MoneyAI()
        result = ai.categorize_transaction(
            description = transaction.description,
            amount = transaction.amount,
            transaction_type = transaction.type.value
        )

        print(f"AI Result: {result}")

        if result["is_ai_categorized"]:
            transaction.category = result["category"]
            transaction.is_ai_categorize = True
            transaction.updated_at = utc_now()

            session.add(transaction)
            session.commit()
            session.refresh(transaction)

        return {
            "success": result["is_ai_categorized"],
            "category": result["category"],
            "confidence": result["confidence"],
            "message": "จัดหมวดหมู่สำเร็จ" if result["is_ai_categorized"] else "ไม่สามารถจัดหมวดหมู่ได้"
        }
    
    except Exception as e:
        print(f"Categoriization Error: {e}")
        return {
            "success": False,
            "category": "อื่นๆ",
            "confidence": 0.0,
            "message": f"เกิดข้อผิดพลาด: {str(e)}"
        }

# Pagnition 
@router.get("/me", response_model = TransactionPaginatedResponse)
async def get_current_query_user_transaction(
    page: int = 1,
    limit: int = 25,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    total_count = session.exec(
        select(func.count(Transaction.id)).where(Transaction.user_id == current_user.id)
    ).one()
    total_page = (total_count + (limit - 1)) // limit
    has_next = page < total_page
    has_prev = page > 1
    skip = (page - 1) * limit
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user.id).offset(skip).limit(limit)
    ).all()

    transaction_responses = []
    for transaction in transactions:
        transaction_response = TransactionRead(
            id = str(transaction.id),
            user_id = str(transaction.user_id),
            amount = transaction.amount,
            type = transaction.type,
            category = transaction.category,
            note = transaction.note,
            description = transaction.description,
            transaction_date = transaction.transaction_date,
            is_ai_categorize = transaction.is_ai_categorize,
            created_at = transaction.created_at.isoformat(),
            updated_at = transaction.updated_at.isoformat() if transaction.updated_at else None
        )
        transaction_responses.append(transaction_response)

    return TransactionPaginatedResponse(
        data = transaction_responses,
        pagination = PaginationInfo(
            page = page,
            limit = limit,
            total = total_count,
            pages = total_page,
            has_next = has_next,
            has_prev = has_prev
        )
    )