import uuid
import logging
import time
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
from fastapi import UploadFile
from app.core.config import settings
from app.ai_coaching.services.openai_service import analyze_pronunciation_feedback
from app.ai_coaching.services.audio_file_service import (
    convert_audio_to_wav,
    get_audio_duration_seconds,
)
from app.ai_coaching.schemas.azure_speech_schema import (
    ProblemWordAudioResponse,
    PronunciationAssessmentResponse,
    SttResponse,
    TtsResponse,
)

logger = logging.getLogger(__name__)

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
    started_at = time.perf_counter()

    if not audio_file.filename:
        raise ValueError("Audio filename is required.")

    await audio_file.seek(0)
    file_content = await audio_file.read()

    if not file_content:
        raise ValueError("Audio file is empty.")

    saved_path = UPLOAD_DIR / f"{uuid.uuid4()}_{audio_file.filename}"

    with saved_path.open("wb") as buffer:
        buffer.write(file_content)

    logger.info(
        "Saved uploaded audio file. filename=%s content_type=%s saved_path=%s size=%s duration_seconds=%s elapsed_ms=%s",
        audio_file.filename,
        audio_file.content_type,
        saved_path,
        len(file_content),
        get_audio_duration_seconds(saved_path),
        int((time.perf_counter() - started_at) * 1000),
    )

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
    started_at = time.perf_counter()

    logger.info(
        "Starting Azure STT recognition. audio_path=%s audio_size=%s duration_seconds=%s",
        saved_path,
        saved_path.stat().st_size if saved_path.exists() else None,
        get_audio_duration_seconds(saved_path),
    )

    speech_config = _create_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=str(saved_path))

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        language="en-US",
    )

    result = recognizer.recognize_once_async().get()

    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        no_match_details = None
        cancellation_details = None

        if result.reason == speechsdk.ResultReason.NoMatch:
            no_match_details = speechsdk.NoMatchDetails.from_result(result)

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails.from_result(result)

        logger.warning(
            "Azure STT did not recognize speech. audio_path=%s elapsed_ms=%s reason=%s no_match_reason=%s cancellation_reason=%s cancellation_error=%s",
            saved_path,
            int((time.perf_counter() - started_at) * 1000),
            result.reason,
            getattr(no_match_details, "reason", None),
            getattr(cancellation_details, "reason", None),
            getattr(cancellation_details, "error_details", None),
        )
        return SttResponse(recognizedText="")

    logger.info(
        "Azure STT recognition completed. audio_path=%s elapsed_ms=%s recognized_text_length=%s",
        saved_path,
        int((time.perf_counter() - started_at) * 1000),
        len(result.text or ""),
    )

    return SttResponse(recognizedText=result.text)


def assess_pronunciation_from_path(
    saved_path: Path,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    started_at = time.perf_counter()

    if not reference_text.strip():
        raise ValueError("Reference text is required.")

    logger.info(
        "Starting Azure pronunciation assessment. audio_path=%s audio_size=%s duration_seconds=%s reference_text_length=%s",
        saved_path,
        saved_path.stat().st_size if saved_path.exists() else None,
        get_audio_duration_seconds(saved_path),
        len(reference_text),
    )

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
        no_match_details = None
        cancellation_details = None

        if result.reason == speechsdk.ResultReason.NoMatch:
            no_match_details = speechsdk.NoMatchDetails.from_result(result)

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails.from_result(result)

        logger.warning(
            "Azure pronunciation assessment did not recognize speech. audio_path=%s elapsed_ms=%s reason=%s no_match_reason=%s cancellation_reason=%s cancellation_error=%s",
            saved_path,
            int((time.perf_counter() - started_at) * 1000),
            result.reason,
            getattr(no_match_details, "reason", None),
            getattr(cancellation_details, "reason", None),
            getattr(cancellation_details, "error_details", None),
        )

        stt_fallback = recognize_speech_from_path(saved_path)
        fallback_text = stt_fallback.recognizedText or ""

        if fallback_text.strip():
            logger.warning(
                "Pronunciation assessment failed but STT fallback recognized speech. audio_path=%s recognized_text_length=%s",
                saved_path,
                len(fallback_text),
            )

            feedback_result = analyze_pronunciation_feedback(
                reference_text=reference_text,
                recognized_text=fallback_text,
                accuracy_score=0,
                fluency_score=0,
                completeness_score=0,
                pronunciation_score=0,
            )

            return PronunciationAssessmentResponse(
                recognizedText=fallback_text,
                accuracyScore=0,
                fluencyScore=0,
                completenessScore=0,
                pronunciationScore=0,
                feedback=feedback_result.get("feedback"),
                problemWords=feedback_result.get("problemWords", []),
            )

        return PronunciationAssessmentResponse(
            recognizedText="",
            accuracyScore=0,
            fluencyScore=0,
            completenessScore=0,
            pronunciationScore=0,
            feedback=DEFAULT_NO_SPEECH_FEEDBACK,
            problemWords=[],
        )

    pronunciation_result = speechsdk.PronunciationAssessmentResult(result)

    recognized_text = result.text

    if not recognized_text.strip():
        logger.warning(
            "Azure pronunciation assessment returned blank recognized text. audio_path=%s elapsed_ms=%s",
            saved_path,
            int((time.perf_counter() - started_at) * 1000),
        )

        stt_fallback = recognize_speech_from_path(saved_path)
        fallback_text = stt_fallback.recognizedText or ""

        if fallback_text.strip():
            feedback_result = analyze_pronunciation_feedback(
                reference_text=reference_text,
                recognized_text=fallback_text,
                accuracy_score=0,
                fluency_score=0,
                completeness_score=0,
                pronunciation_score=0,
            )

            return PronunciationAssessmentResponse(
                recognizedText=fallback_text,
                accuracyScore=0,
                fluencyScore=0,
                completenessScore=0,
                pronunciationScore=0,
                feedback=feedback_result.get("feedback"),
                problemWords=feedback_result.get("problemWords", []),
            )

        return PronunciationAssessmentResponse(
            recognizedText="",
            accuracyScore=0,
            fluencyScore=0,
            completenessScore=0,
            pronunciationScore=0,
            feedback=DEFAULT_NO_SPEECH_FEEDBACK,
            problemWords=[],
        )

    accuracy_score = pronunciation_result.accuracy_score
    fluency_score = pronunciation_result.fluency_score
    completeness_score = pronunciation_result.completeness_score
    pronunciation_score = pronunciation_result.pronunciation_score

    # LLM 분석
    feedback_started_at = time.perf_counter()

    feedback_result = analyze_pronunciation_feedback(
        reference_text=reference_text,
        recognized_text=recognized_text,
        accuracy_score=accuracy_score,
        fluency_score=fluency_score,
        completeness_score=completeness_score,
        pronunciation_score=pronunciation_score,
    )

    logger.info(
        "Azure pronunciation assessment completed. audio_path=%s total_elapsed_ms=%s feedback_elapsed_ms=%s recognized_text_length=%s pronunciation_score=%s",
        saved_path,
        int((time.perf_counter() - started_at) * 1000),
        int((time.perf_counter() - feedback_started_at) * 1000),
        len(recognized_text),
        pronunciation_score,
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
    wav_path = convert_audio_to_wav(saved_path)
    return recognize_speech_from_path(wav_path)


async def assess_pronunciation(
    audio_file: UploadFile,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    saved_path = await save_upload_file(audio_file)

    wav_path = convert_audio_to_wav(saved_path)

    return assess_pronunciation_from_path(
        wav_path,
        reference_text,
    )


async def recognize_and_assess_pronunciation(
    audio_file: UploadFile,
    reference_text: str,
) -> PronunciationAssessmentResponse:
    started_at = time.perf_counter()

    saved_path = await save_upload_file(audio_file)

    wav_path = convert_audio_to_wav(saved_path)

    logger.info(
        "Converted pronunciation audio. original_path=%s original_size=%s original_duration_seconds=%s wav_path=%s wav_size=%s wav_duration_seconds=%s",
        saved_path,
        saved_path.stat().st_size if saved_path.exists() else None,
        get_audio_duration_seconds(saved_path),
        wav_path,
        wav_path.stat().st_size if wav_path.exists() else None,
        get_audio_duration_seconds(wav_path),
    )

    response = assess_pronunciation_from_path(
        saved_path=wav_path,
        reference_text=reference_text,
    )

    logger.info(
        "Pronunciation assessment request completed. original_filename=%s elapsed_ms=%s recognized_text_length=%s",
        audio_file.filename,
        int((time.perf_counter() - started_at) * 1000),
        len(response.recognizedText or ""),
    )

    return response


def synthesize_problem_word(word: str) -> ProblemWordAudioResponse:
    if not word.strip():
        raise ValueError("Word is required.")

    tts_response = synthesize_text_to_audio(word)

    return ProblemWordAudioResponse(
        word=word,
        audioUrl=tts_response.audioUrl,
    )
