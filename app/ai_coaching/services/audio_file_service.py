from pathlib import Path
import logging
import subprocess
import time

logger = logging.getLogger(__name__)

def convert_audio_to_wav(input_path: str | Path) -> Path:
    input_file = Path(input_path)

    if input_file.suffix.lower() == ".wav":
        return input_file

    output_file = input_file.with_suffix(".wav")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        str(output_file),
    ]

    started_at = time.perf_counter()
    logger.info(
        "Starting audio conversion. input=%s output=%s",
        input_file,
        output_file,
    )

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.exception(
            "Audio conversion failed. input=%s output=%s elapsed_ms=%s stderr=%s",
            input_file,
            output_file,
            int((time.perf_counter() - started_at) * 1000),
            exc.stderr,
        )
        raise

    logger.info(
        "Audio conversion completed. input=%s output=%s elapsed_ms=%s output_size=%s",
        input_file,
        output_file,
        int((time.perf_counter() - started_at) * 1000),
        output_file.stat().st_size if output_file.exists() else None,
    )

    return output_file


def get_audio_duration_seconds(input_path: str | Path) -> float | None:
    input_file = Path(input_path)

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_file),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning(
            "Audio duration probe failed. input=%s error=%s",
            input_file,
            exc,
        )
        return None

    try:
        return float(result.stdout.strip())
    except ValueError:
        logger.warning(
            "Audio duration probe returned invalid output. input=%s output=%s",
            input_file,
            result.stdout,
        )
        return None
