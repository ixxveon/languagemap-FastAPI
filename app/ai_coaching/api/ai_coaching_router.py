from fastapi import APIRouter, File, Form, UploadFile
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
    return await recognize_and_assess_pronunciation(
        audio_file=audio_file,
        reference_text=reference_text,)

# =========================
# YouTube
# =========================
@router.post("/youtube-search", response_model=YoutubeSearchResponse)
def create_youtube_search(request: YoutubeSearchRequest,) -> YoutubeSearchResponse:
    return search_youtube_videos(
        keyword=request.keyword,
        max_results=request.maxResults,)