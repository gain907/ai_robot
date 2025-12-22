"""
[AI 비서 Nova - 메모리 기능 포함 버전]

이 코드는 다음과 같은 고급 기능을 포함하고 있습니다:
1. 기억하기 (Memory): 대화 내용을 'important(중요)'와 'Not Important(비중요)'로 나누어 JSON 파일에 저장합니다.
2. 문맥 파악: 과거의 대화 기록(History)을 AI에게 함께 보내주어, 이전 내용을 기억하고 대답하게 합니다.
3. 형식 제어: AI가 [상태, 답변] 형태로 대답하도록 강제하여, 프로그램이 중요도를 판단할 수 있게 합니다.

작성일: 2025.12.23
"""

# ------------------- 1. 라이브러리 불러오기 (도구 상자) -------------------

import io  # 파일을 저장하지 않고 메모리에서 바로 다루기 위한 도구
import json  # 대화 내용을 파일로 저장하고 불러오기 위한 도구 (JSON 형식)
import os  # 파일이 실제로 존재하는지 확인하기 위한 도구
from typing import Literal  # 코드의 타입을 명확히 하기 위한 도구

import google.generativeai as genai  # [뇌] 구글 Gemini AI
import pygame  # [스피커] 소리 재생
import speech_recognition as sr  # [귀] 음성 인식
from openai import OpenAI  # [입] OpenAI 음성 합성 (TTS)

# [API 키 설정]
# 1. 구글 Gemini API 키 (지능 담당)
genai.configure(api_key="여기에_GEMINI_API_키를_넣으세요")

# 2. OpenAI API 키 (목소리 담당 - 유료)
client = OpenAI(api_key="여기에_OPENAI_API_키를_넣으세요")

# 대화 내용을 저장할 파일 이름 설정
MEMORY_FILE = "nova-memory.json"

# ------------------- 3. AI 페르소나 및 규칙 설정 (프롬프트) -------------------
# AI에게 역할과 "반드시 지켜야 할 응답 형식"을 가르칩니다.
NOVA_PROMPT = (
    """
    당신은 나의 개인 AI 비서 'Nova(노바)'입니다. 간결하고 유용한 정보를 제공하세요.

    지침:
    1. 질문을 받으면 자신을 'Nova'라고 소개하세요.
    2. 답변은 한국어로 정중하고 간결하게, 핵심만 전달하세요. 긴 설명은 피하세요.
    3. 대화의 맥락을 유지하세요.
    4. 사용자의 이름이 알려진 경우 'OOO 님'이라고 부르고, 아니면 정중한 인사를 사용하세요.
    5. 사용자의 모든 입력에 대해 정보를 다음과 같이 분류하세요:
       - Important (중요): 개인 정보(이름, 생일, 위치, 취미), 긴급/중요한 문제, '일정', '긴급' 등의 키워드나 강한 감정 표현이 포함된 경우.
       - Not Important (중요하지 않음): 일상적인 잡담, 사소한 주제, 단순한 사실 확인 등.

    응답 형식은 반드시 다음과 같아야 합니다: [Status, Response]
    예시:
    [Important, 네 홍길동 님, 중요한 일정으로 메모했습니다.]
    [Not Important, 날씨가 참 좋네요! 공유해 주셔서 감사합니다.]
    """
)


# ------------------- 4. 기능 정의: 듣기 (Speech-to-Text) -------------------
def speech_to_text():
    """
    [귀] 마이크로 소리를 듣고 한국어 텍스트로 변환합니다.
    """
    recognizer = sr.Recognizer()

    # 중요: 컴퓨터마다 마이크 번호(0, 1, 2...)가 다를 수 있습니다. 오류 시 변경 필요.
    microphone_index = 2

    try:
        with sr.Microphone(device_index=microphone_index) as source:
            # 주변 잡음을 1초간 분석해서 제거
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("듣고 있습니다... (말씀하세요)")

            # 음성 듣기 시작
            audio = recognizer.listen(source)

            # 구글 서버를 통해 한국어('ko-KR')로 변환
            text = recognizer.recognize_google(audio, language='ko-KR')
            print("사용자: " + text)
            return text

    except (sr.UnknownValueError, sr.RequestError) as exp:
        print(f"오디오를 처리할 수 없습니다: {exp}")
    except Exception as exp:
        print(f"오류가 발생했습니다: {exp}")


# ------------------- 5. 기능 정의: 생각하기 (AI Response) -------------------
def ai_model_response(u_input, conversation):
    """
    [뇌] 사용자의 질문과 '과거 대화 기록'을 함께 AI에게 보냅니다.
    """
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    # 현재 어떤 모델이 작동 중인지 확인하는 디버깅용 코드
    print(f" 현재 작동 중인 실제 모델 이름: {model.model_name}")

    # [프롬프트(규칙) + 과거 기록 + 현재 질문]을 합쳐서 질문합니다.
    full_prompt = f"{NOVA_PROMPT}\n대화 기록:\n{conversation}\n사용자: {u_input}"

    response = model.generate_content(full_prompt)
    return response.text.strip()


# ------------------- 6. 기능 정의: 말하기 (Text-to-Speech) -------------------
def text_to_speech(text):
    """
    [입] OpenAI를 사용하여 텍스트를 자연스러운 음성으로 변환합니다.
    """
    # voice 옵션: alloy, echo, fable, onyx, nova, shimmer
    # 한국어 발음이 비교적 자연스러운 'nova' 목소리 선택
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"

    try:
        # OpenAI 서버에 음성 생성 요청
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        # 생성된 음성 데이터를 재생 함수로 전달
        play_audio(response.read())
    except Exception as e:
        print(f"TTS 오류: {e}")


def play_audio(audio_bytes):
    """
    [스피커] 메모리에 있는 오디오 데이터를 직접 재생합니다.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()

    # 오디오 재생이 끝날 때까지 기다립니다. (안 기다리면 다음 코드로 바로 넘어감)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# ------------------- 7. 기능 정의: 기억 관리 (Memory System) -------------------

def load_memory():
    """
    저장된 JSON 파일에서 대화 기록을 불러옵니다.
    """
    if os.path.exists(MEMORY_FILE):
        # 한글 깨짐 방지를 위해 encoding='utf-8' 필수
        with open(MEMORY_FILE, "r", encoding='utf-8') as file:
            return json.load(file)
    # 파일이 없으면 빈 기억장소를 만듭니다.
    return {"Important": [], "Not Important": []}


def save_memory(memory):
    """
    대화 기록을 JSON 파일로 저장합니다.
    """
    with open(MEMORY_FILE, "w", encoding='utf-8') as file:
        # indent=4: 보기 좋게 들여쓰기, ensure_ascii=False: 한글 그대로 저장
        json.dump(memory, file, indent=4, ensure_ascii=False)


def update_memory(u_input, nova_response, flag):
    """
    새로운 대화를 중요도(flag)에 따라 분류하여 저장합니다.
    flag: 'Important' 또는 'Not Important'
    """
    memory = load_memory()

    # 혹시 파일 형식이 깨졌을 경우를 대비한 안전장치
    if not isinstance(memory, dict):
        memory = {"Important": [], "Not Important": []}

    # 저장할 데이터 한 세트
    entry = {"user_input": u_input, "ai_response": nova_response}

    # 중요도에 따라 분류 저장
    if flag == "Important":
        memory["Important"].append(entry)
    else:
        # 키가 없는 경우 생성
        if "Not Important" not in memory:
            memory["Not Important"] = []
        memory["Not Important"].append(entry)

    save_memory(memory)


def get_conversation_history():
    """
    AI에게 보내주기 위해 저장된 기억을 하나의 문자열로 합칩니다.
    """
    memory = load_memory()

    if not isinstance(memory, dict) or "Important" not in memory or "Not Important" not in memory:
        return ""

    # 저장된 모든 대화를 "[사용자: ... AI: ...]" 형식으로 변환하여 합침
    history = "\n".join(
        f"[사용자: {entry['user_input']} AI: {entry['ai_response']}]"
        for key in ["Important", "Not Important"]
        for entry in memory[key]
    )
    return history


# ------------------- 8. 메인 프로그램 실행 -------------------

if __name__ == "__main__":
    pygame.init()  # 오디오 초기화

    # 1. 시작 인사
    greeting = "안녕하세요, 오늘 무엇을 도와드릴까요?"
    print(f"AI: {greeting}")
    text_to_speech(greeting)

    # 2. 무한 대화 루프
    while True:
        try:
            # [단계 1] 사용자 말 듣기
            user_input = speech_to_text()

            if user_input:
                # [단계 2] 기억 불러오기 및 AI 생각하기
                conversation_history = get_conversation_history()
                ai_response = ai_model_response(user_input, conversation_history)

                # [단계 3] AI 응답 해석하기 (형식: [Status, Response])
                # 예: "[Important, 알겠습니다]" -> status="Important", req_response="알겠습니다"
                if ai_response.startswith("[") and "]" in ai_response:
                    try:
                        # 대괄호([])를 제거하고 쉼표(,)를 기준으로 나눔
                        clean_response = ai_response.strip('[]')
                        status, req_response = clean_response.split(", ", 1)
                    except ValueError:
                        # 형식이 안 맞으면 기본값 처리
                        status = "Not Important"
                        req_response = ai_response
                else:
                    status = "Not Important"
                    req_response = ai_response

                # [단계 4] 기억 업데이트 및 말하기
                update_memory(user_input, req_response, status)
                print(f"AI 응답 ({status}): {req_response}")
                text_to_speech(req_response)

        except KeyboardInterrupt:
            # Ctrl+C를 누르면 종료
            print("종료합니다...")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")