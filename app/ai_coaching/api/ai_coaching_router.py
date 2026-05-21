import logging
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from app.ai_coaching.schemas.azure_speech_schema import (
    ProblemWordAudioRequest,
    ProblemWordAudioResponse,
    PronunciationAssessmentResponse,
    SttResponse,
    TtsRequest,
    TtsResponse,)
from app.ai_coaching.schemas.openai_schema import (
    CoachingScriptRequest,
    CoachingScriptResponse,
    FinalFeedbackRequest,
    FinalFeedbackResponse,
    YoutubeKeywordsRequest,
    YoutubeKeywordsResponse,)
from app.ai_coaching.schemas.youtube_schema import (
    VideoSummaryRequest,
    VideoSummaryResponse,
    YoutubeSearchRequest,
    YoutubeSearchResponse,)
from app.ai_coaching.services.azure_speech_service import (
    recognize_and_assess_pronunciation,
    recognize_speech_from_file,
    synthesize_problem_word,
    synthesize_text_to_audio,)
from app.ai_coaching.services.openai_service import (
    generate_coaching_script,
    generate_final_feedback,
    generate_youtube_keywords,
    summarize_video_with_llm,)
from app.ai_coaching.services.youtube_service import search_youtube_videos

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ai-coaching",
    tags=["AI Coaching"],)

# =========================
# OpenAI
# =========================
@router.post("/coaching-script", response_model=CoachingScriptResponse)
def create_coaching_script(request: CoachingScriptRequest,) -> CoachingScriptResponse:
    return generate_coaching_script(request)

@router.post("/final-feedback", response_model=FinalFeedbackResponse)
def create_final_feedback(request: FinalFeedbackRequest,) -> FinalFeedbackResponse:
    return generate_final_feedback(request)

@router.post("/youtube-keywords", response_model=YoutubeKeywordsResponse)
def create_youtube_keywords(request: YoutubeKeywordsRequest,) -> YoutubeKeywordsResponse:
    return generate_youtube_keywords(request)

@router.post("/video-summary", response_model=VideoSummaryResponse)
def create_video_summary(request: VideoSummaryRequest,) -> VideoSummaryResponse:
    return summarize_video_with_llm(request)

# =========================
# Azure Speech
# =========================
@router.post("/tts", response_model=TtsResponse)
def create_tts(request: TtsRequest,) -> TtsResponse:
    return synthesize_text_to_audio(request.text)

@router.post("/problem-word-audio", response_model=ProblemWordAudioResponse)
def create_problem_word_audio(request: ProblemWordAudioRequest,) -> ProblemWordAudioResponse:
    return synthesize_problem_word(request.word)

@router.post("/stt", response_model=SttResponse)
async def create_stt(audio_file: UploadFile = File(...),) -> SttResponse:
    return await recognize_speech_from_file(audio_file)

@router.post(
    "/pronunciation-assessment",
    response_model=PronunciationAssessmentResponse,)
async def create_pronunciation_assessment(reference_text: str = Form(...),audio_file: UploadFile = File(...),
) -> PronunciationAssessmentResponse:
    logger.info(
        "Pronunciation assessment endpoint request received. filename=%s content_type=%s reference_text_length=%s",
        audio_file.filename,
        audio_file.content_type,
        len(reference_text or ""),
    )

    try:
        response = await recognize_and_assess_pronunciation(
            audio_file=audio_file,
            reference_text=reference_text,
        )
    except Exception:
        logger.exception(
            "Pronunciation assessment endpoint failed. filename=%s content_type=%s",
            audio_file.filename,
            audio_file.content_type,
        )
        return JSONResponse(
            status_code=500,
            content={
                "recognizedText": "",
                "accuracyScore": 0,
                "fluencyScore": 0,
                "completenessScore": 0,
                "pronunciationScore": 0,
                "feedback": "음성이 명확하게 인식되지 않았습니다.",
                "problemWords": [],
                "nextAssistantText": None,
                "nextAssistantAudioUrl": None,
                "detail": "pronunciation-assessment failed",
            },
        )

    logger.info(
        "Pronunciation assessment endpoint response serialize. filename=%s response=%s",
        audio_file.filename,
        response.model_dump(),
    )

    return response

# =========================
# YouTube
# =========================
@router.post("/youtube-search", response_model=YoutubeSearchResponse)
def create_youtube_search(request: YoutubeSearchRequest,) -> YoutubeSearchResponse:
    return search_youtube_videos(
        keyword=request.keyword,
        max_results=request.maxResults,)
