# app/db/base.py

from sqlmodel import SQLModel

# USERS
from app.features.users.models import User

#chat
from app.features.chats.models import Room, RoomMember, Message

# AUTH
from app.features.auth.models import RefreshToken

# SESSIONS
from app.features.sessions.models import Session

# PAYMENTS
from app.features.payments.models import Payment

# MODERATION
from app.features.moderation.models import ModerationReport

# REVIEWS
from app.features.reviews.models import Review

# TUTORS
from app.features.tutors.models import TutorProfile

# COURSES
from app.features.courses.models import Course, TutorCourse

# AI
from app.features.ai.models import AIConversation, AIMessage, AICredit

# AUDIT
from app.features.audit.models import AuditLog
