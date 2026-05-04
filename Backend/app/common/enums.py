from enum import Enum

class UserRole(str, Enum):
    student = "student"
    tutor = "tutor"
    admin = "admin"

class chatMemberRole(str, Enum):
    member = "member"
    admin = "admin"

class SessionStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class ReportStatus(str, Enum):
    pending = "pending"
    reviewed = "reviewed"
    resolved = "resolved"
    dismissed = "dismissed"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"

class AiChatRole(str,Enum):
    user = "user"
    assistant = "assistant"

