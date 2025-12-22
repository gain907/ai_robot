"""
[AI 로봇 제어 - 무료/한국어 버전]

수정 내용:
1. OpenAI 제거 -> gTTS(무료) 적용
2. 릴레이 제거 -> 모터 3개 제어 (좌, 우, 머리)
3. 한국어 음성 인식 및 대화 지원
"""

# ------------------- Import Libraries -------------------

import io
import threading
from typing import Literal

import google.generativeai as genai
import pygame
import speech_recognition as sr
from cvzone.SerialModule import SerialObject
from gtts import gTTS  # [무료] 구글 텍스트-음성 변환
import cv2

# ------------------- Configurations -------------------

# [API 키 설정]
# 여기에 본인의 Gemini API 키를 넣어주세요.
genai.configure(api_key="여기에_GEMINI_API_키를_넣으세요")

# 영상 파일 경로 확인 필요
video_path = '../Resources/Casual Eyes.mp4'

# 아두이노 통신 설정 (데이터 3개 전송)
arduino = SerialObject(digits=3)

# [초기 상태 설정]
# 순서: [왼쪽 팔(L), 오른쪽 팔(R), 머리(H)]
# 릴레이가 빠졌으므로 3개만 관리합니다.
# (참고: 180, 0, 90은 일반적인 로봇 팔 내리는 각도입니다. 본인 로봇에 맞춰 수정하세요.)
state = [180, 0, 90]

# ------------------- AI Prompt (한국어 명령 설정) -------------------

control_prompt = (
    """
    사용자의 한국어 명령을 해석하여 다음 규칙에 따라 '숫자'만 반환하세요.

    [규칙]:
    - "멈춰", "초기화", "리셋", "제자리" -> "0"
    - "왼쪽 팔", "왼손", "1번 모터" -> "1"
    - "오른쪽 팔", "오른손", "2번 모터" -> "2"
    - "머리", "고개", "3번 모터" -> "3"
    - "전체 이동", "다 움직여", "만세", "인사" -> "4"

    [주의]:
    - 설명이나 다른 말은 하지 말고 오직 숫자(0, 1, 2, 3, 4) 중 하나만 반환하세요.
    """
)


# ------------------- Play Video (Full-Screen Playback) -------------------
def play_video(video_path):
    """
    영상을 전체 화면으로 재생하는 함수 (스레드로 실행됨)
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"오류: 영상을 찾을 수 없습니다: {video_path}")
        return

    # 화면 해상도 설정 (본인 모니터에 맞게 수정)
    screen_width, screen_height = 1536, 864

    cv2.namedWindow('Full Screen', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Full Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # 듀얼 모니터 사용 시 창 이동 (필요 없으면 주석 처리)
    cv2.moveWindow('Full Screen', 1790, -50)

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 무한 반복
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (screen_width, screen_height))
            cv2.imshow('Full Screen', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return


# ------------------- Speech-to-Text Function (한국어) -------------------

def speech_to_text():
    recognizer = sr.Recognizer()
    # 마이크 번호가 안 맞으면 0, 1, 2 등으로 변경해보세요.
    microphone_index = 1
    try:
        with sr.Microphone(device_index=microphone_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("듣고 있습니다... (말씀하세요)")
            audio = recognizer.listen(source)

            # [중요] 한국어 인식 설정 (language='ko-KR')
            text = recognizer.recognize_google(audio, language='ko-KR')
            print("사용자: " + text)
            return text

    except (sr.UnknownValueError, sr.RequestError) as exp:
        print(f"오디오 인식 실패: {exp}")
    except Exception as exp:
        print(f"오류 발생: {exp}")


# ------------------- AI Response Function -------------------

def ai_model_response(u_input):
    """
    Gemini에게 명령어를 숫자로 변환해달라고 요청
    """
    model = genai.GenerativeModel('gemini-2.5-flash-lite')  # 혹은 gemini-2.5-flash-lite
    full_prompt = f"{control_prompt}\n사용자: {u_input}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text.strip()


# ------------------- Text-to-Speech Function (무료) -------------------

def text_to_speech(text):
    """
    gTTS(무료)를 사용하여 텍스트를 음성으로 재생
    """
    try:
        # 한국어(lang='ko') 설정
        tts = gTTS(text=text, lang='ko', slow=False)

        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        play_audio(fp.read())
    except Exception as e:
        print(f"TTS 오류: {e}")


def play_audio(audio_bytes):
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# 영상 재생 스레드 시작
video_thread = threading.Thread(target=play_video, args=(video_path,))
video_thread.start()

# ------------------- Main Program -------------------

if __name__ == "__main__":
    pygame.init()

    # 시작 인사
    text_to_speech("안녕하세요. 무엇을 도와드릴까요?")

    while True:
        try:
            user_input = speech_to_text()

            if user_input:
                # AI가 명령어를 숫자로 변환 (예: "왼손 들어" -> "1")
                action_number = ai_model_response(user_input)
                print(f"Action Number: {action_number}")

                # [상태 업데이트 로직]
                if action_number == "0":  # 초기화
                    state = [180, 0, 90]
                    text_to_speech("모든 장치를 초기화했습니다.")

                elif action_number == "1":  # 왼쪽 팔 (90도)
                    state[0] = 90
                    text_to_speech("왼쪽 팔을 움직였습니다.")

                elif action_number == "2":  # 오른쪽 팔 (90도)
                    state[1] = 90
                    text_to_speech("오른쪽 팔을 움직였습니다.")

                elif action_number == "3":  # 머리 (90도)
                    state[2] = 90
                    text_to_speech("머리를 움직였습니다.")

                # (4, 5번 전구 기능은 삭제됨)

                elif action_number == "4":  # 전체 이동
                    state = [90, 90, 90]
                    text_to_speech("모든 모터를 움직였습니다.")

                # 아두이노로 데이터 전송 (3개 값)
                arduino.sendData(state)

        except KeyboardInterrupt:
            print("종료합니다...")
            text_to_speech("안녕히 계세요.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")