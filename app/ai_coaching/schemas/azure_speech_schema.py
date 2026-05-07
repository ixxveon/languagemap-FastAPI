from pydantic import BaseModel, Field

# =========================
# TTS
# =========================
class TtsRequest(BaseModel):
    text: str = Field(...,json_schema_extra={"example": "Hi, welcome! What would you like to order today?"},)

class TtsResponse(BaseModel):
    audioUrl: str

# =========================
# STT
# =========================
class SttResponse(BaseModel):
    recognizedText: str

# =========================
# PronunciationProblemWord
# =========================
class PronunciationProblemWord(BaseModel):
    word: str
    score: float | None = None
    feedback: str | None = None

# =========================
# Pronunciation Assessment
# =========================
class PronunciationAssessmentResponse(BaseModel):
    recognizedText: str
    accuracyScore: float | None = None
    fluencyScore: float | None = None
    completenessScore: float | None = None
    pronunciationScore: float | None = None
    feedback: str | None = None
    problemWords: list[PronunciationProblemWord] = []
# =========================
# Problem Word Audio
# =========================
class ProblemWordAudioRequest(BaseModel):
    word: str = Field(...,json_schema_extra={"example": "almond"},)

class ProblemWordAudioResponse(BaseModel):
    word: str
    audioUrl: str