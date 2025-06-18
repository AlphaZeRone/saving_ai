from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select, func
from typing import Optional, List

from models.user import User
from api.auth import require_auth
from models.base import utc_now
from core.ai_service import MoneyAI
from core.database import get_session
from models.chat import Conversation, Message, ConversationStatus, MessageSender, MessageRating, ConversationRead, ConversationUpdate, MessageCreate, MessageRead, MessageUpdate, RatingRead, RatingCreate, ChatResponse, generate_topic_from_message

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
    