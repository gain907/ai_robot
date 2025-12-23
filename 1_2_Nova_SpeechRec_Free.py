"""
Basic Ai speech code (Free Version)
- Brain: Google Gemini (Free)
- Voice: Google gTTS (Free)

pip install gTTS 설치해야함

"""
# ------------------- Import Libraries -------------------

import io
import google.generativeai as genai
import pygame
import speech_recognition as sr
from gtts import gTTS  # [추가됨] 무료 TTS 라이브러리

# ------------------- Configurations -------------------

# [중요] 구글 API 키만 있으면 됩니다 (OpenAI 키 필요 없음)
genai.configure(api_key="")

# ------------------- AI Prompt -------------------

nova_prompt = (
    """
    당신은 '노바(Nova)'라는 이름의 개인 AI 로봇 비서입니다. 
    다음 지침을 따르세요:
    1. 정체성: 자신을 '로봇 비서 노바'라고 소개하세요.
    2. 간결함: 대답은 항상 짧고 간결한 한국어 존댓말로 하세요.
    3. 태도: 항상 친절하고 예의 바르게 행동하세요.
    """
)


# ------------------- Speech-to-Text (듣기) -------------------

def speech_to_text():
    recognizer = sr.Recognizer()
    microphone_index = 2  # 마이크 번호 (안 되면 0, 2 등으로 변경)
    try:
        with sr.Microphone(device_index=microphone_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("\n 듣고 있습니다... (말씀해주세요)")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language='ko-KR')
            print(f" 사용자: {text}")
            return text
    except sr.UnknownValueError:
        print("x (소리를 못 들었습니다)")
    except sr.RequestError:
        print("x (인터넷 연결을 확인하세요)")
    except Exception as e:
        print(f"x (오류): {e}")


# ------------------- AI Response (생각하기) -------------------

def ai_model_response(u_input):
    # 아까 확인한 무료 모델 이름 사용 (목록에 떴던 것 중 하나)
    # 예: gemini-2.5-flash 또는 gemini-1.5-flash
    model = genai.GenerativeModel('gemini-2.5-flash-lite')  # gemini-1.5-flash

    full_prompt = f"{nova_prompt}\nUser: {u_input}"
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"죄송해요, 생각하는 중에 오류가 났어요. ({e})"


# ------------------- Text-to-Speech (말하기 - 무료 버전) -------------------

def text_to_speech(text):
    """
    gTTS(무료)를 사용하여 텍스트를 음성으로 변환합니다.
    """
    try:
        # lang='ko' : 한국어 설정
        # slow=False : 정상 속도
        tts = gTTS(text=text, lang='ko', slow=False)

        # 파일로 저장하지 않고 메모리에서 바로 재생 (속도 향상)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        play_audio(fp.read())

    except Exception as e:
        print(f"TTS 오류: {e}")

# 메모리에 있는 오디오 데이터(파일 아님)를 스피커로 재생하고, 재생이 끝날 때까지 기다리는 함수
def play_audio(audio_bytes):
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# ------------------- Main Program -------------------

if __name__ == "__main__":
    pygame.init()
    print("로봇이 시작되었습니다! (무료 버전)")

    # 첫 인사
    text_to_speech("안녕하세요. 저는 노바입니다.")

    while True:
        user_input = speech_to_text()

        if user_input:
            ai_response = ai_model_response(user_input)
            print(f"노바: {ai_response}")
            text_to_speech(ai_response)