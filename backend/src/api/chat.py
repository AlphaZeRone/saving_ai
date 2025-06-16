from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select, func
from typing import Optional, List

from models.user import User
from api.auth import require_auth
from models.base import utc_now
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
    # TODO: Implement database logic
    pass