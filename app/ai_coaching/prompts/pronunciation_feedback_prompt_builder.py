def build_pronunciation_feedback_prompt(
    reference_text: str,
    recognized_text: str,
    accuracy_score: float | None,
    fluency_score: float | None,
    completeness_score: float | None,
    pronunciation_score: float | None,
) -> str:
    return f"""
You are an English pronunciation coach for a language learning app.

Compare the expected sentence and the learner's recognized speech.
Evaluate only based on the provided data.

[Expected Sentence]
{reference_text}

[Recognized Sentence]
{recognized_text}

[Azure Pronunciation Scores]
accuracyScore: {accuracy_score}
fluencyScore: {fluency_score}
completenessScore: {completeness_score}
pronunciationScore: {pronunciation_score}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

Rules:
- Write feedback in Korean.
- feedback must be one short sentence.
- problemWords must be an array of objects.
- Each problem word object must contain:
  - word: English word
  - score: number from 0 to 100 or null
  - feedback: short Korean feedback sentence
- problemWords must contain 0 to 5 items.
- Do not invent words that are unrelated to the expected or recognized sentence.
- Prioritize words that are missing, misrecognized, incomplete, or likely mispronounced.
- If the recognized sentence is very different from the expected sentence, include the most important missing or misrecognized words.
- If pronunciationScore is below 60, feedback should clearly say more pronunciation practice is needed.
- If pronunciationScore is 80 or above and there are no obvious issues, return an empty problemWords list.

Output JSON format:
{{
  "feedback": "전체적으로 말했지만 일부 단어 발음을 더 또렷하게 연습하면 좋습니다.",
  "problemWords": [
    {{
      "word": "almond",
      "score": 72,
      "feedback": "almond 발음을 더 또렷하게 연습하면 좋습니다."
    }}
  ]
}}
""".strip()