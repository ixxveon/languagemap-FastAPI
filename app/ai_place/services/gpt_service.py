import os
from openai import OpenAI
from dotenv import load_dotenv

from app.ai_place.utils.prompt_builder import (
    build_mission_start_prompt,
    build_chat_prompt,
    build_evaluation_prompt,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_mission_start_message(request):
    messages = build_mission_start_prompt(
        level=request.level,
        scenario_prompt=request.scenarioPrompt,
        scenario_category=request.scenarioCategory,
        mission_title=request.missionTitle,
        mission_description=request.missionDescription,
    )

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        max_completion_tokens=1000,
        temperature=0.2
    )

    return response.choices[0].message.content


def create_chat_message(request):
    messages = build_chat_prompt(
        scenario_prompt=request.scenarioPrompt,
        scenario_category=request.scenarioCategory,
        mission_title=request.missionTitle,
        mission_description=request.missionDescription,
        user_message=request.userMessage,
        messages=request.messages[-10:]
    )

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        max_completion_tokens=1000,
        temperature=0.2
    )

    return response.choices[0].message.content


def create_evaluation(request):
    messages = build_evaluation_prompt(
        scenario_prompt=request.scenarioPrompt,
        scenario_category=request.scenarioCategory,
        messages=request.messages
    )

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        max_completion_tokens=1000,
        temperature=0.2
    )

    return response.choices[0].message.content