from fastapi import FastAPI
# from app.api import api_router

app = FastAPI(title="CampusIQ API")

# app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
