from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.features.auth.routes import router as auth_router
from app.features.admin.routes import router as admin_router

app = FastAPI(title="CampusIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)


# app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
