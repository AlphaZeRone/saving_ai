from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from sqlmodel import Session, select, func
from typing import Optional, List

from models.user import User
from api.auth import require_auth
from models.base import utc_now
from core.database import get_session
from models.chat import Conversation, Message, ConversationStatus, MessageSender

router = APIRouter()

# ===== API Endpoint =======