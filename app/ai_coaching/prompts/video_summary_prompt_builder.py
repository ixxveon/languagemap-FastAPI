def build_video_summary_prompt(
    title: str,
    channel_title: str,
    description: str,
) -> str:
    return f"""
You are a Korean language learning assistant.

Summarize why this YouTube video is useful for English speaking practice.

[Video Title]
{title}

[Channel]
{channel_title}

[Description]
{description}

Return ONLY JSON.
Do not include markdown.

Rules:
- Write in Korean.
- Make the summary specific to this video.
- Do not use a generic repeated sentence.
- Keep it within 1 short Korean sentence.

Format:
{{
  "summary": "..."
}}
""".strip()