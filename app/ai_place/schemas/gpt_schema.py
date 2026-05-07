from pydantic import BaseModel
from typing import List

# 미션 시작
class MissionStartRequest(BaseModel):
    level: str
    scenarioPrompt: str
    scenarioCategory: str
    missionTitle: str
    missionDescription: str


class MissionStartResponse(BaseModel):
    aiMessage: str

# 채팅
class ChatMessage(BaseModel):
    role: str
    message: str

class ChatRequest(BaseModel):
    userMessage: str
    messages: List[ChatMessage]
    missionTitle: str
    missionDescription: str
    scenarioPrompt: str
    scenarioCategory: str

class ChatResponse(BaseModel):
    aiMessage: str

# 미션 완료 및 평가
class EvaluationMessage(BaseModel):
    role: str
    message: str


class EvaluationRequest(BaseModel):
    scenarioPrompt: str
    scenarioCategory: str
    messages: List[EvaluationMessage]


class EvaluationResponse(BaseModel):
    evaluation: str