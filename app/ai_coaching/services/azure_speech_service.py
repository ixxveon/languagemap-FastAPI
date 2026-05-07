import uuid
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
from fastapi import UploadFile
from app.core.config import settings
from app.ai_coaching.services.openai_service import analyze_pronunciation_feedback
from app.ai_coaching.schemas.azure_speech_schema import (
    ProblemWordAudioResponse,
    PronunciationAssessmentResponse,
    SttResponse,
    TtsResponse,
)

AUDIO_DIR = Path("static/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# fallback 메시지 상수화
DEFAULT_NO_SPEECH_FEEDBACK = "음성이 명확하게 인식되지 않았습니다."

def _create_speech_config() -> speechsdk.SpeechConfig:
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.azure_speech_key,
        region=settings.azure_speech_region,
    )
    speech_config.speech_synthesis_voice_name = settings.azure_speech_voice_name
    return speech_config


async def save_upload_file(audio_file: UploadFile) -> Path:
    if not audio_file.filename:
        raise ValueError("Audio filename is required.")

    await audio_file.seek(0)
    file_content = await audio_file.read()

    if not file_content:
        raise ValueError("Audio file is empty.")

    saved_path = UPLOAD_DIR / f"{uuid.uuid4()}_{audio_file.filename}"

    with saved_path.open("wb") as buffer:
        buffer.write(file_content)

    return saved_path


def synthesize_text_to_audio(text: str) -> TtsResponse:
    if not text.strip():
        raise ValueError("Text is required.")

    filename = f"{uuid.uuid4()}.wav"
    file_path = AUDIO_DIR / filename

    speech_config = _create_speech_config()
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(file_path))

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        detail = getattr(result, "error_details", None)
        raise RuntimeError(f"Azure TTS generation failed. detail={detail}")

    return TtsResponse(audioUrl=f"/static/audio/{filename}")


def recognize_speech_from_path(saved_path: Path) -> SttResponse:
    speech_config = _create_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=str(saved_path))

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        language="en-US",
    )

    result = recognizer.recognize_once_async().get()

    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return SttResponse(recognizedText="")

    return SttResponse(recognizedText=result.text)


def assess_pronunciation_from_path(
    saved_path: Path,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    if not reference_text.strip():
        raise ValueError("Reference text is required.")

    speech_config = _create_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=str(saved_path))

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        language="en-US",
    )

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True,
    )

    pronunciation_config.apply_to(recognizer)
    result = recognizer.recognize_once_async().get()

    # Azure 음성 인식 실패
    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return PronunciationAssessmentResponse(
            recognizedText="",
            accuracyScore=None,
            fluencyScore=None,
            completenessScore=None,
            pronunciationScore=None,
            feedback=DEFAULT_NO_SPEECH_FEEDBACK,
            problemWords=[],
        )

    pronunciation_result = speechsdk.PronunciationAssessmentResult(result)

    recognized_text = result.text
    accuracy_score = pronunciation_result.accuracy_score
    fluency_score = pronunciation_result.fluency_score
    completeness_score = pronunciation_result.completeness_score
    pronunciation_score = pronunciation_result.pronunciation_score

    # LLM 분석
    feedback_result = analyze_pronunciation_feedback(
        reference_text=reference_text,
        recognized_text=recognized_text,
        accuracy_score=accuracy_score,
        fluency_score=fluency_score,
        completeness_score=completeness_score,
        pronunciation_score=pronunciation_score,
    )

    return PronunciationAssessmentResponse(
        recognizedText=recognized_text,
        accuracyScore=accuracy_score,
        fluencyScore=fluency_score,
        completenessScore=completeness_score,
        pronunciationScore=pronunciation_score,
        feedback=feedback_result.get("feedback"),
        problemWords=feedback_result.get("problemWords", []),
    )


async def recognize_speech_from_file(audio_file: UploadFile) -> SttResponse:
    saved_path = await save_upload_file(audio_file)
    return recognize_speech_from_path(saved_path)


async def assess_pronunciation(
    audio_file: UploadFile,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    saved_path = await save_upload_file(audio_file)

    return assess_pronunciation_from_path(
        saved_path=saved_path,
        reference_text=reference_text,
    )


async def recognize_and_assess_pronunciation(
    audio_file: UploadFile,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    saved_path = await save_upload_file(audio_file)

    return assess_pronunciation_from_path(
        saved_path=saved_path,
        reference_text=reference_text,
    )


def synthesize_problem_word(word: str) -> ProblemWordAudioResponse:
    if not word.strip():
        raise ValueError("Word is required.")

    tts_response = synthesize_text_to_audio(word)

    return ProblemWordAudioResponse(
        word=word,
        audioUrl=tts_response.audioUrl,
    )