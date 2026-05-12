# Mapingo FastAPI AI Server

지도 기반 AI 영어 학습 서비스 Mapingo의 AI 서버입니다.

OpenAI 기반 영어 회화 생성 및 AI 학습 기능을 담당합니다.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-AI_Server-009688?style=for-the-badge&logo=fastapi)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI_Server-499848?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?style=for-the-badge&logo=openai)
![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?style=for-the-badge)
![Python-dotenv](https://img.shields.io/badge/Python_Dotenv-Environment-4B8BBE?style=for-the-badge)
![Pydantic Settings](https://img.shields.io/badge/Pydantic_Settings-Config_Management-E92063?style=for-the-badge)
![Notion](https://img.shields.io/badge/Notion-Documentation-000000?style=for-the-badge&logo=notion)

---

## 주요 기능(Main Domains)

- AI 음성 학습 도메인
- AI 채팅 도메인
---

## 레포지토리 구조(Repository Structure)

| Repository | Address |
|---|---|
| language-react | [React Frontend](https://github.com/soo97/languagemap-react.git) |
| language-spring | [Spring Boot API Server](https://github.com/soo97/languagemap-spring.git) |
| language-fastapi | [FastAPI AI Server](https://github.com/soo97/languagemap-FastAPI.git) |

---

## AWS 아키텍쳐(AWS Architecture)

<img width="1627" height="967" alt="image" src="https://github.com/user-attachments/assets/a1f1799b-9b03-40f8-90d3-a3abe20415ef" />

---

## 브랜치 구조(Branch Structure)

| Branch | Description |
|---|---|
| main | 운영 가능한 안정 버전 |
| feature/* | 기능 개발 브랜치 |
| fix/* | 기능 수정 브랜치 |

---

## 프로젝트 규칙(Project Rules)


- `main.py`에서 FastAPI 앱과 라우터를 관리한다.
- 기능별 코드는 `app/{feature}` 단위로 분리한다.
- 각 기능은 `api`, `schemas`, `services` 구조를 따른다.
- 요청/응답 형식은 Pydantic 스키마로 정의한다.
- 비즈니스 로직과 외부 API 호출은 `services`에서 처리한다.
- 환경설정 값은 `.env` 기반으로 관리한다.
- 정적 파일은 `static` 디렉터리에서 관리한다.

---

## 커밋 규칙(Commit Rules)

```text
feat: 기능 추가
fix: 버그 수정
style: 코드 포맷/스타일 변경
chore: 기타 설정
design: UI/UX 변경
rename: 이름 변경
remove: 삭제
refactor: 리팩토링
build: 빌드 변경
```

---

## 기술 스택(Tech Stack)

| Category | Stack |
|---|---|
| AI Server | FastAPI, Python |
| ASGI Server | Uvicorn |
| AI API | OpenAI API |
| Data Validation | Pydantic |
| Environment Management | Python-dotenv, Pydantic Settings |
| Collaboration Tools | GitHub, Notion, Swagger, ERDCloud |

---

## 폴더 구조(Folder Structure)

```text
languagemap-FastAPI
├─ app
│  ├─ ai_coaching
│  │  ├─ api
│  │  ├─ prompts
│  │  ├─ schemas
│  │  └─ services
│  ├─ ai_place
│  │  ├─ api
│  │  ├─ schemas
│  │  ├─ services
│  │  └─ utils
│  └─ core
├─ static
│  ├─ audio
│  └─ uploads
├─ main.py
└─ requirements.txt
```

## 네이밍 컨벤션(Naming Convention)

| Layer | Rule |
|---|---|
| Router | ~Router |
| Service | ~Service |
| Schema | ~Schema |
| Model | snake_case |
| Prompt | ~Prompt |

---

## API 컨벤션(API Convention)

- REST API 기반 설계
- JSON 기반 Request / Response 처리
- Pydantic 기반 데이터 검증
- 공통 응답 형식 사용
- Spring Server 응답 구조 통일

---

## 응답 컨벤션(Response Convention)

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

## 프롬프트 규칙

- Role, Instruction, Context, Output Format 구조로 작성한다.
- JSON 응답이 필요한 경우 JSON만 반환하게 한다.
- 마크다운, 코드블록, 부가 설명은 금지한다.
- 장소, 이전 대화, 평가 결과 등 입력 컨텍스트를 반영한다.
- 결과는 학습용으로 실용적이고 자연스럽게 작성한다.
- 대화 확장 시 기존 흐름과 의미를 유지한다.
- 출력 언어와 형식, 개수 조건을 프롬프트에서 명확히 지정한다.

---

## 환경 변수(Environment Variables)

env 설정

```env
OPENAI_API_KEY=
OPENAI_MOCK_MODE=
OPENAI_CHAT_MODEL=
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
AZURE_SPEECH_ENDPOINT=
AZURE_SPEECH_VOICE_NAME=
YOUTUBE_API_KEY=
```

---

## 보안 규칙(Secret Rules)

- .env 파일 GitHub 업로드 금지
- OpenAI API Key 외부 노출 금지
- 환경 변수 로컬 개별 관리

---

## 레포지토리 복제(Clone Repository)

```bash
git clone https://github.com/soo97/languagemap-FastAPI.git
```

---

## 팀원 및 역할(Team Members)

| 이름 | 역할 | 기능 구현 |
|---|---|---|
| 임수현 | 팀장 | (추가 예정) |
| 고은별 | 팀원 | // |
| 마은재 | 팀원 | // |
| 이가연 | 팀원 | // |
| 이현재 | 팀원 | // |
| 홍순찬 | 팀원 | // |
