from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select, func
from typing import Optional, List

from models.user import User
from api.auth import require_auth
from models.base import utc_now
from core.ai_service import MoneyAI
from core.database import get_session
from models.chat import Conversation, PaginationInfo, MessagePaginated, Message, ConversationStatus, MessageSender, MessageRating, ConversationRead, ConversationUpdate, MessageCreate, MessageRead, MessageUpdate, RatingRead, RatingCreate, ChatResponse, generate_topic_from_message, ConversationPaginatedResponse, ConversationWithLatestMessage, ConversationWithLatestMessageResponse

router = APIRouter()

# ===== API Endpoint =======
# Create Message
@router.post("/messages", response_model = ChatResponse, status_code = status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    # เช็คว่า Message นี้มี Conversation แล้วหรืออยัง
    conversation = None

    if message_data.conversation_id:
        # มี conversation id ก็ใช้ที่มีอยู่
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == message_data.conversation_id)
            .where(Conversation.user_id == current_user.id)
            .where(Conversation.status != ConversationStatus.DELETED)
        ).first()

        if not conversation:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "ไม่พบบทสนทนานี้"
            )
        
    else :
        # message ไม่มี conversation สร้าง conversation ใหม่
        topic = generate_topic_from_message(message_data.content)
        conversation = Conversation(
            user_id = current_user.id,
            topic = topic,
            total_message = 0,
            status = ConversationStatus.ACTIVE
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Create next_index
    next_index = conversation.total_message + 1

    # Create new message object
    new_message = Message(
        conversation_id = conversation.id,
        content = message_data.content,
        sender_type = MessageSender.USER,
        message_index = next_index
    )

    conversation.total_message += 1
    session.add(new_message)
    session.add(conversation)
    session.commit()
    session.refresh(new_message)

    recent_message = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.message_index.desc())
        .limit(5)
    ).all()

    recent_message = list(reversed(recent_message))

    conversation_history = ""
    for msg in recent_message:
        sender = "ผู้ใช้" if msg.sender_type == MessageSender.USER else "AI"
        conversation_history += f"{sender}: {msg.content}\n"

    ai_service = MoneyAI()
    ai_result = ai_service.generate_chat_response(
        user_message = message_data.content,
        conversation_history = conversation_history
    )

    ai_message = Message(
        conversation_id = conversation.id,
        content = ai_result["content"],
        sender_type = MessageSender.AI,
        message_index = conversation.total_message + 1,
        token_used = ai_result["tokens_used"],
        response_time_ms = ai_result["response_time_ms"],
        ai_model = ai_result["model"]
    )

    conversation.total_message += 1
    session.add(ai_message)
    session.add(conversation)
    session.commit()
    session.refresh(ai_message)

    return ChatResponse(
        user_message = MessageRead.model_validate(new_message),
        ai_message = MessageRead.model_validate(ai_message),
        conversation = ConversationRead.model_validate(conversation),
        recent_messages = [MessageRead.model_validate(msg) for msg in recent_message]
    )
    
# Create List Conversation 
@router.get("/conversations", response_model = ConversationWithLatestMessageResponse, status_code = status.HTTP_200_OK)
async def list_conversations(
    page: int = 1,
    limit: int = 25,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    total_count = session.exec(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    ).one()
    total_page = (total_count + (limit - 1)) // limit
    has_next = page < total_page
    has_prev = page > 1
    skip = (page - 1) * limit
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    conversation_ids = [conv.id for conv in conversations]

    latest_message = session.exec(
        select(Message)
        .where(Message.conversation_id.in_(conversation_ids))
        .where(Message.message_index.in_(
            select(func.max(Message.message_index))
            .where(Message.conversation_id.in_(conversation_ids))
            .group_by(Message.conversation_id)
        ))
    ).all()
        
    message_lookup = {msg.conversation_id: msg for msg in latest_message}

    result_data = []
    for conv in conversations:
        latest_msg = message_lookup.get(conv.id)
        result_data.append(ConversationWithLatestMessage(
            conversation = ConversationRead.model_validate(conv),
            latest_message = MessageRead.model_validate(latest_msg) if latest_msg else None
        ))
    
    return ConversationWithLatestMessageResponse(
        data = result_data,
        pagination = PaginationInfo(
            page = page,
            limit = limit,
            total = total_count,
            pages = total_page,
            has_next = has_next,
            has_prev = has_prev
        )
    )

# ====== Get message in conversation =======
@router.get("/conversations/{conversation_id}/messages", response_model = MessagePaginated, status_code = status.HTTP_200_OK)
async def get_conversation_messages(
    conversation_id: str,
    page: int = 1,
    limit: int = 25,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    import uuid
    conversation_uuid = uuid.UUID(conversation_id)
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_uuid)
        .where(Conversation.user_id == current_user.id)
        .where(Conversation.status != ConversationStatus.DELETED)
    ).first()

    if not conversation:
        raise HTTPException(status_code = 404, detail = "ไม่พบบทสนทนานี้")
    
    total_count = conversation.total_message
    total_page = (total_count + (limit - 1)) // limit
    has_next = page < total_page
    has_prev = page > 1
    skip = (page - 1) * limit

    message = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.message_index.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    result_data = []

    message_reversed = list(reversed(message))

    for msg in message_reversed:
        result_data.append(MessageRead.model_validate(msg))

    return MessagePaginated(
        data = result_data,
        pagination = PaginationInfo(
            page = page,
            limit = limit,
            total = total_count,
            pages = total_page,
            has_next = has_next,
            has_prev = has_prev
        )
    )

# ====== Update Conversation =======
@router.put("/conversations/{conversation_id}", response_model=ConversationRead, status_code=status.HTTP_200_OK)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    import uuid
    conversation_uuid = uuid.UUID(conversation_id)
    
    # ตรวจสอบว่า conversation นี้เป็นของ user นี้
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_uuid)
        .where(Conversation.user_id == current_user.id)
        .where(Conversation.status != ConversationStatus.DELETED)
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบบทสนทนานี้"
        )
    
    # Update ข้อมูลที่ส่งมา
    if update_data.topic is not None:
        conversation.topic = update_data.topic
    
    if update_data.status is not None:
        conversation.status = update_data.status
    
    # อัพเดท updated_at
    conversation.updated_at = utc_now()
    
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    
    return ConversationRead.model_validate(conversation)

# ====== Delete Conversation (Soft Delete) =======
@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    import uuid
    conversation_uuid = uuid.UUID(conversation_id)
    
    # ตรวจสอบว่า conversation นี้เป็นของ user นี้
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_uuid)
        .where(Conversation.user_id == current_user.id)
        .where(Conversation.status != ConversationStatus.DELETED)
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบบทสนทนานี้"
        )
    
    # Soft delete - เปลี่ยน status เป็น DELETED
    conversation.status = ConversationStatus.DELETED
    conversation.updated_at = utc_now()
    
    session.add(conversation)
    session.commit()
