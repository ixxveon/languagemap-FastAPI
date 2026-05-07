from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.ai_coaching.api.ai_coaching_router import router as ai_coaching_router
from app.ai_place.api.gpt_router import router as gpt_router

app = FastAPI(
    title="LanguageMap FastAPI",
    description="LanguageMap AI Coaching API Server",
    version="1.0.0",)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(ai_coaching_router)
app.include_router(gpt_router)

@app.get("/")
def read_root():
    return {"message": "LanguageMap FastAPI server is running"}