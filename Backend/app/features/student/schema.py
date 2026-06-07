from pydantic import BaseModel


class SessionsStats(BaseModel):
    this_week: int
    delta: int


class LearningStats(BaseModel):
    hours_this_week: float


class TutorsStats(BaseModel):
    active_this_week: int


class AIStats(BaseModel):
    questions_this_week: int


class StudentStatsResponse(BaseModel):
    sessions: SessionsStats
    learning: LearningStats
    tutors: TutorsStats
    ai: AIStats