import json
from openai import OpenAI
from app.core.config import settings
from app.ai_coaching.prompts.coaching_script_prompt_builder import build_coaching_script_prompt
from app.ai_coaching.prompts.final_feedback_prompt_builder import build_final_feedback_prompt
from app.ai_coaching.prompts.youtube_keywords_prompt_builder import build_youtube_keywords_prompt
from app.ai_coaching.prompts.video_summary_prompt_builder import build_video_summary_prompt
from app.ai_coaching.prompts.pronunciation_feedback_prompt_builder import build_pronunciation_feedback_prompt
from app.ai_coaching.schemas.youtube_schema import (
    VideoSummaryRequest,
    VideoSummaryResponse,
)
from app.ai_coaching.schemas.openai_schema import (
    CoachingScriptItem,
    CoachingScriptRequest,
    CoachingScriptResponse,
    FeedbackSection,
    FinalFeedbackRequest,
    FinalFeedbackResponse,
    ProblemWord,
    PronunciationSection,
    YoutubeKeywordsRequest,
    YoutubeKeywordsResponse,
)

# =========================
# OpenAI Client
# =========================
client = OpenAI(api_key=settings.openai_api_key)

# =========================
# Internal JSON Helpers
# =========================
def _extract_text(response) -> str:
    return response.output_text

def _safe_json_loads(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1

        if 0 <= start < end:
            return json.loads(text[start:end])

        raise

def _request_json(prompt: str) -> dict:
    if not prompt.strip():
        raise ValueError("Prompt is required.")

    response = client.responses.create(
        model=settings.openai_chat_model,
        input=prompt,)

    return _safe_json_loads(_extract_text(response))

# =========================
# Coaching Script
# =========================
def generate_coaching_script(request: CoachingScriptRequest) -> CoachingScriptResponse:
    if settings.openai_mock_mode:
        return CoachingScriptResponse(
            messages=[
                CoachingScriptItem(
                    role="ASSISTANT",
                    message="Hi, welcome! What would you like to order today?",),
                CoachingScriptItem(
                    role="USER",
                    message="I would like a latte with almond milk, please.",),
                CoachingScriptItem(
                    role="ASSISTANT",
                    message="Sure. Would you like it hot or iced?",),
                CoachingScriptItem(
                    role="USER",
                    message="I would like it iced, please.",),
            ]
        )

    prompt = build_coaching_script_prompt(
        option_type=request.optionType,
        place_name=request.placeName,
        country=request.country,
        city=request.city,
        place_address=request.placeAddress,
        evaluation=request.evaluation,
        previous_messages=request.previousMessages,)

    data = _request_json(prompt)

    return CoachingScriptResponse(
        messages=[
            CoachingScriptItem(
                role=item["role"],
                message=item["message"],)
            for item in data["messages"]
        ]
    )

# =========================
# Pronunciation Feedback
# =========================
def analyze_pronunciation_feedback(
    reference_text: str,
    recognized_text: str,
    accuracy_score: float | None,
    fluency_score: float | None,
    completeness_score: float | None,
    pronunciation_score: float | None,
) -> dict:
    if not recognized_text.strip():
        return {
            "feedback": "음성이 명확하게 인식되지 않았습니다.",
            "problemWords": [],
        }

    if settings.openai_mock_mode:
        return {
            "feedback": "전체적으로 말했지만 일부 단어 발음을 더 또렷하게 연습하면 좋습니다.",
            "problemWords": [
                {
                    "word": "almond",
                    "score": pronunciation_score,
                    "feedback": "almond 발음을 더 또렷하게 연습하면 좋습니다.",
                }
            ],
        }

    prompt = build_pronunciation_feedback_prompt(
        reference_text=reference_text,
        recognized_text=recognized_text,
        accuracy_score=accuracy_score,
        fluency_score=fluency_score,
        completeness_score=completeness_score,
        pronunciation_score=pronunciation_score,
    )

    data = _request_json(prompt)

    raw_problem_words = data.get("problemWords", [])

    normalized_problem_words = []
    for item in raw_problem_words:
        if isinstance(item, str):
            normalized_problem_words.append({
                "word": item,
                "score": None,
                "feedback": f"{item} 발음을 더 또렷하게 연습하면 좋습니다.",
            })
        elif isinstance(item, dict):
            normalized_problem_words.append({
                "word": item.get("word", ""),
                "score": item.get("score"),
                "feedback": item.get("feedback"),
            })

    return {
        "feedback": data.get("feedback", ""),
        "problemWords": normalized_problem_words,
    }

# =========================
# Final Feedback
# =========================
def generate_final_feedback(request: FinalFeedbackRequest) -> FinalFeedbackResponse:
    if not request.messages:
        raise ValueError("Conversation messages are required.")

    if settings.openai_mock_mode:
        avg_score = 0

        if request.pronunciationResults:
            scores = [
                r.pronunciationScore
                for r in request.pronunciationResults
                if r.pronunciationScore is not None
            ]
            avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score >= 80:
            level = "GOOD"
        elif avg_score >= 60:
            level = "CHECK"
        else:
            level = "NEEDS_IMPROVEMENT"

        return FinalFeedbackResponse(
            totalScore=round(avg_score),
            summaryFeedback="발음 점수가 낮아 일부 단어와 문장 완성도를 다시 연습하면 좋습니다.",
            naturalness=FeedbackSection(
                level=level,
                comment="인식된 문장을 기준으로 자연스러움을 평가했습니다.",
            ),
            flow=FeedbackSection(
                level=level,
                comment="대화 흐름은 실제 응답 내용과 질문의 연결성을 기준으로 평가했습니다.",
            ),
            pronunciation=PronunciationSection(
                level=level,
                comment="발음 점수와 문제 단어를 기준으로 추가 연습이 필요합니다.",
                problemWords=[
                    ProblemWord(word="almond", audioUrl=None),
                ],
            ),
        )

    prompt = build_final_feedback_prompt(
        messages=request.messages,
        pronunciation_results=request.pronunciationResults,
    )

    data = _request_json(prompt)

    return FinalFeedbackResponse(**data)

# =========================
# YouTube Keywords
# =========================
def generate_youtube_keywords(request: YoutubeKeywordsRequest,) -> YoutubeKeywordsResponse:
    if not request.finalFeedback.strip():
        raise ValueError("Final feedback is required.")

    if settings.openai_mock_mode:
        return YoutubeKeywordsResponse(
            keywords=[
                "cafe English ordering politely",
                "English pronunciation almond",
                "travel English cafe dialogue",]
        )

    prompt = build_youtube_keywords_prompt(
        final_feedback=request.finalFeedback,)
    data = _request_json(prompt)
    return YoutubeKeywordsResponse(**data)

# =========================
# Video Summary
# =========================
def summarize_video_with_llm(request: VideoSummaryRequest) -> VideoSummaryResponse:
    if not request.title.strip():
        raise ValueError("Video title is required.")

    if settings.openai_mock_mode:
        return VideoSummaryResponse(
            summary=f"'{request.title}' 영상은 실제 표현과 상황별 말하기 연습에 도움이 됩니다."
        )

    prompt = build_video_summary_prompt(
        title=request.title,
        channel_title=request.channelTitle,
        description=request.description,
    )

    data = _request_json(prompt)
    return VideoSummaryResponse(**data)