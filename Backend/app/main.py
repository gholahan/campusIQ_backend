from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging
from app.features.auth.routes import router as auth_router
from app.features.admin.routes import router as admin_router
from app.features.tutors.routes import router as tutors_router
from app.features.sessions.routes import router as session_router
from app.features.student.routes import router as student_router
from app.features.ai.routes import router as ai_router
from app.features.ai.graph import setup_graph

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with setup_graph():
        yield


app = FastAPI(title="CampusIQ API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://campus-iq-edu.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(tutors_router)
app.include_router(session_router)
app.include_router(student_router)
app.include_router(ai_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
