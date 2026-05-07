from typing import List
from pydantic import BaseModel, Field

# =========================
# Common
# =========================
class PreviousMessage(BaseModel):
    role: str = Field(..., json_schema_extra={"example": "USER"})
    message: str = Field(..., json_schema_extra={"example": "I would like a latte, please."})

# =========================
# Coaching Script
# =========================
class CoachingScriptRequest(BaseModel):
    optionType: str = Field(..., json_schema_extra={"example": "WORD"})
    placeName: str = Field(..., json_schema_extra={"example": "Cafe Stage 888"})
    country: str = Field(..., json_schema_extra={"example": "Australia"})
    city: str = Field(..., json_schema_extra={"example": "Sydney"})
    placeAddress: str = Field(..., json_schema_extra={"example": "Near George St."})
    evaluation: str = Field(default="", json_schema_extra={"example": "표현은 자연스럽고 주문 의도 전달이 잘 되었어요."})
    previousMessages: List[PreviousMessage] = Field(default_factory=list)

class CoachingScriptItem(BaseModel):
    role: str
    message: str

class CoachingScriptResponse(BaseModel):
    messages: List[CoachingScriptItem]

# =========================
# Final Feedback
# =========================
class PronunciationResult(BaseModel):
    expectedText: str
    recognizedText: str
    accuracyScore: float | None = None
    fluencyScore: float | None = None
    completenessScore: float | None = None
    pronunciationScore: float | None = None
    problemWords: list[str] = []

class FinalFeedbackRequest(BaseModel):
    messages: List[PreviousMessage] = Field(default_factory=list)
    pronunciationResults: List[PronunciationResult] = Field(default_factory=list)

class FeedbackSection(BaseModel):
    level: str
    comment: str

class ProblemWord(BaseModel):
    word: str
    audioUrl: str | None = None

class PronunciationSection(BaseModel):
    level: str
    comment: str
    problemWords: List[ProblemWord] = Field(default_factory=list)

class FinalFeedbackResponse(BaseModel):
    totalScore: int
    summaryFeedback: str
    naturalness: FeedbackSection
    flow: FeedbackSection
    pronunciation: PronunciationSection

# =========================
# Recommend Sentences
# =========================
class RecommendSentencesRequest(BaseModel):
    finalFeedback: str

class RecommendSentencesResponse(BaseModel):
    sentences: List[str]

# =========================
# YouTube Keywords
# =========================
class YoutubeKeywordsRequest(BaseModel):
    finalFeedback: str

class YoutubeKeywordsResponse(BaseModel):
    keywords: List[str]