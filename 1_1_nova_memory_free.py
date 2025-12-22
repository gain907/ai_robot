"""
[AI 비서 Nova - 100% 무료 버전]

이 코드는 유료인 OpenAI 기능을 제거하고, 무료 라이브러리인 gTTS를 사용합니다.
1. 듣기: 구글 음성 인식 (무료)
2. 생각하기: 구글 Gemini (무료 등급 사용)
3. 말하기: 구글 gTTS (무료 - 구글 번역기 목소리)
4. 기억하기: 대화 내용 저장 및 중요도 분류

작성일: 2025.12.23
"""

# ------------------- 1. 라이브러리 불러오기 -------------------
import io  # 데이터 메모리 처리
import json  # 데이터 저장 (JSON)
import os  # 파일 관리
from typing import Literal  # 타입 힌트

import google.generativeai as genai  # [뇌] 구글 Gemini AI
import pygame  # [스피커] 오디오 재생
import speech_recognition as sr  # [귀] 음성 인식
from gtts import gTTS  # [입] 무료 음성 합성 (Google Text-to-Speech)

# [API 키 설정]
# 여기에 본인의 Gemini API 키를 넣어주세요.
genai.configure(api_key="여기에_GEMINI_API_키를_넣으세요")


# 기억을 저장할 파일 이름
MEMORY_FILE = "nova-memory.json"

# ------------------- 3. AI 프롬프트 (성격 설정) -------------------
NOVA_PROMPT = (
    """
    당신은 나의 개인 AI 비서 'Nova(노바)'입니다. 

    [지침]:
    1. 답변은 **한국어**로 정중하고 간결하게, 핵심만 전달하세요.
    2. 자신을 소개할 때는 'Nova'라고 하세요.
    3. 사용자의 이름이 있다면 이름을 부르세요.
    4. 사용자의 입력 내용을 분석하여 **'Important(중요)'** 또는 **'Not Important(중요하지 않음)'**으로 분류하세요.
       - Important: 이름, 생일, 취미, 일정, 약속, 긴급한 내용.
       - Not Important: 단순한 인사, 잡담, 날씨 질문 등.

    [응답 형식 - 반드시 지킬 것]:
    [Status, Response]

    예시:
    [Important, 네 홍길동 님, 회의 일정을 저장했습니다.]
    [Not Important, 반갑습니다! 오늘 기분은 어떠신가요?]
    """
)


# ------------------- 4. 기능 정의: 듣기 (STT) -------------------
def speech_to_text():
    """
    마이크로 소리를 듣고 한국어 텍스트로 변환합니다. (무료)
    """
    recognizer = sr.Recognizer()

    # 마이크 번호가 안 맞으면 0, 1, 2 등으로 바꿔보세요.
    microphone_index = 2

    try:
        with sr.Microphone(device_index=microphone_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("듣고 있습니다... (말씀하세요)")

            audio = recognizer.listen(source)

            # 구글 무료 음성 인식 (한국어 설정)
            text = recognizer.recognize_google(audio, language='ko-KR')
            print("사용자: " + text)
            return text

    except (sr.UnknownValueError, sr.RequestError) as exp:
        print(f"인식 실패: {exp}")
    except Exception as exp:
        print(f"오류 발생: {exp}")


# ------------------- 5. 기능 정의: 생각하기 (LLM) -------------------
def ai_model_response(u_input, conversation):
    """
    Gemini에게 질문하고 답변을 받습니다. (무료 티어)
    """
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    full_prompt = f"{NOVA_PROMPT}\n대화 기록:\n{conversation}\n사용자: {u_input}"

    response = model.generate_content(full_prompt)
    return response.text.strip()


# ------------------- 6. 기능 정의: 말하기 (Free TTS) -------------------
def text_to_speech(text):
    """
    gTTS(무료)를 사용하여 텍스트를 음성으로 읽어줍니다.
    OpenAI 대신 구글 번역기 목소리를 사용합니다.
    """
    try:
        # gTTS 객체 생성 (lang='ko'는 한국어, slow=False는 정상 속도)
        tts = gTTS(text=text, lang='ko', slow=False)

        # 파일로 저장하지 않고 메모리(BytesIO)에 담습니다.
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)  # 파일 포인터를 맨 앞으로 이동

        # 재생 함수 호출
        play_audio(fp.read())

    except Exception as e:
        print(f"TTS 오류: {e}")


def play_audio(audio_bytes):
    """
    메모리에 있는 오디오 데이터를 재생합니다.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# ------------------- 7. 기능 정의: 기억 관리 (Memory) -------------------

def load_memory():
    """
    기억 파일 불러오기
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding='utf-8') as file:
            return json.load(file)
    return {"Important": [], "Not Important": []}


def save_memory(memory):
    """
    기억 파일 저장하기 (한글 깨짐 방지)
    """
    with open(MEMORY_FILE, "w", encoding='utf-8') as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


def update_memory(u_input, nova_response, flag):
    """
    대화 내용 저장 및 분류
    """
    memory = load_memory()

    if not isinstance(memory, dict):
        memory = {"Important": [], "Not Important": []}

    entry = {"user_input": u_input, "ai_response": nova_response}

    if flag == "Important":
        memory["Important"].append(entry)
    else:
        if "Not Important" not in memory:
            memory["Not Important"] = []
        memory["Not Important"].append(entry)

    save_memory(memory)


def get_conversation_history():
    """
    AI에게 전달할 과거 기록 문자열 생성
    """
    memory = load_memory()
    if not isinstance(memory, dict) or "Important" not in memory:
        return ""

    history = "\n".join(
        f"[User: {entry['user_input']} AI: {entry['ai_response']}]"
        for key in ["Important", "Not Important"]
        for entry in memory.get(key, [])
    )
    return history


def delete_not_important_memory():
    """
    중요하지 않은 기억 삭제 (청소)
    """
    memory = load_memory()
    if "Not Important" in memory and memory["Not Important"]:
        memory["Not Important"] = []
        save_memory(memory)
        print("메모리 정리: 중요하지 않은 기억 삭제됨.")


def check_memory_percentage():
    """
    메모리 사용량 확인
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding='utf-8') as file:
            data = json.load(file)
        full_length = len(json.dumps(data))
        max_length = 10000
        return (full_length / max_length) * 100, full_length
    return 0, 0


# ------------------- 8. 메인 프로그램 실행 -------------------
if __name__ == "__main__":
    pygame.init()

    start_msg = "안녕하세요, 저는 무료 AI 비서 노바입니다."
    print(f"AI: {start_msg}")
    text_to_speech(start_msg)

    try:
        while True:
            try:
                # 1. 듣기
                user_input = speech_to_text()

                if user_input:
                    # 2. 생각하기
                    conversation_history = get_conversation_history()
                    ai_response = ai_model_response(user_input, conversation_history)

                    # 3. 형식 분석 [Status, Response]
                    if ai_response.startswith("[") and "]" in ai_response:
                        try:
                            clean_response = ai_response.strip('[]')
                            status, req_response = clean_response.split(", ", 1)
                        except ValueError:
                            status = "Not Important"
                            req_response = ai_response
                    else:
                        status = "Not Important"
                        req_response = ai_response

                    # 4. 말하기 & 저장
                    update_memory(user_input, req_response, status)
                    print(f"AI 응답 ({status}): {req_response}")
                    text_to_speech(req_response)

            except KeyboardInterrupt:
                print("종료합니다.")
                break
            except Exception as e:
                print(f"오류: {e}")

    finally:
        percentage, _ = check_memory_percentage()
        print(f"메모리 사용량: {percentage:.2f}%")

        if percentage > 10:
            print("메모리 정리 중...")
            delete_not_important_memory()