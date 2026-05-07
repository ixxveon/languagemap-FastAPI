from fastapi import APIRouter

from app.ai_place.schemas.gpt_schema import (
    MissionStartRequest,
    MissionStartResponse,
    ChatRequest,
    ChatResponse,
    EvaluationRequest,
    EvaluationResponse,
)
from app.ai_place.services.gpt_service import (
    create_mission_start_message,
    create_chat_message,
    create_evaluation,
)

router = APIRouter(prefix="/gpt", tags=["GPT"])


@router.post("/mission/start", response_model=MissionStartResponse)
def mission_start(request: MissionStartRequest):
    ai_message = create_mission_start_message(request)
    return MissionStartResponse(aiMessage=ai_message)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    ai_message = create_chat_message(request)
    return ChatResponse(aiMessage=ai_message)


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest):
    evaluation = create_evaluation(request)
    return EvaluationResponse(evaluation=evaluation)