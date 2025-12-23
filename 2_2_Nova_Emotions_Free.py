"""
Speech with emotions (Free Version - User Style)
* Brain: Google Gemini 2.5 Flash (Free)
* Voice: Google gTTS (Free)
* OS: Windows
* Style: Thread-based video playback (User Request)

pip install gTTS 설치해야함

"""

# ------------------- Import Libraries -------------------

import io
import os
import threading
from time import sleep

import cv2
import pygame
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS  # [중요] 무료 TTS 라이브러리
from cvzone.SerialModule import SerialObject

# ------------------- Configuration -------------------

# [중요] 구글 API 키만 있으면 됩니다 (OpenAI 키 필요 없음)
# genai.configure(api_key="여기에_구글_API_키_입력")
genai.configure(api_key="")
# ------------------- Global Variables -------------------

# Create a Serial object
try:
    # 윈도우는 보통 자동 연결되지만, 안 되면 port='COM3' 등 입력
    arduino = SerialObject(digits=3)
except:
    print(" Arduino not connected")
    arduino = None

last_positions = [180, 0, 90]
switch_video = False
# 스레드들끼리 소통하기 위한 '신호등(스위치)'을 만드는 역할
stop_video_event = threading.Event()

# ------------------- AI Prompt (Korean) -------------------

nova_prompt = (
    """
    당신은 '노바(Nova)'라는 이름의 개인 AI 로봇 비서입니다. 
    다음 지침을 따르세요:
    1. 정체성: 자신을 '로봇 비서 노바'라고 소개하세요.
    2. 간결함: 대답은 항상 짧고 간결한 한국어 존댓말로 하세요.
    3. 태도: 항상 친절하고 예의 바르게 행동하세요.
    """
)


# ========================= Speech Recognition ==============================

def speech_to_text():
    recognizer = sr.Recognizer()
    microphone_index = 1  # 윈도우에서는 보통 생략 가능하거나 1번
    try:
        # with sr.Microphone() as source:  # 윈도우: 장치 자동 선택
        with sr.Microphone(device_index=microphone_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("\n 듣고 있습니다...")
            audio = recognizer.listen(source, phrase_time_limit=5)
            # 한국어 인식 설정
            text = recognizer.recognize_google(audio, language='ko-KR')
            print("You said: " + text)
            return text
    except sr.UnknownValueError:
        pass
    except Exception as exp:
        print(f"Error: {exp}")


# ------------------- AI Response Function -------------------

def ai_model_response(u_input):
    # 최신 무료 모델 사용
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    full_prompt = f"{nova_prompt}\nUser: {u_input}"
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except:
        return "죄송해요. 생각하는 데 오류가 났어요."


# ------------------- Text-to-Speech (Free Version) -------------------

def text_to_speech(text):
    """
    gTTS(무료)를 사용하여 음성 생성
    """
    try:
        # lang='ko': 한국어, slow=False: 정상 속도
        tts = gTTS(text=text, lang='ko', slow=False)

        # 파일 저장 없이 메모리에서 바로 재생 (속도 향상)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        play_audio(fp.read())
    except Exception as e:
        print(f"TTS Error: {e}")


def play_audio(audio_bytes):
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# =========================== Gesture Integration ================================

def move_servo(target_positions, delay=0.01):
    global last_positions
    if arduino is None: return

    max_steps = max(abs(target_positions[i] - last_positions[i]) for i in range(3))
    for step in range(max_steps):
        current = [
            last_positions[i] + (step + 1) * (target_positions[i] - last_positions[i]) // max_steps
            if abs(target_positions[i] - last_positions[i]) > step else last_positions[i]
            for i in range(3)
        ]
        arduino.sendData(current)
        sleep(delay)
    last_positions = target_positions[:]


def reset_arms_sequentially():
    """팔을 하나씩 내려서 아두이노 꺼짐 방지"""
    global last_positions
    print("Resetting arms...")
    current_left = last_positions[0]
    move_servo([current_left, 0, 90], delay=0.02)
    sleep(0.5)
    move_servo([180, 0, 90], delay=0.02)
    sleep(0.5)


def casual_rest():
    move_servo([180, 0, 90])


def hello_gesture():
    global last_positions
    print("Gesture: Hello")
    move_servo([last_positions[0], 180, last_positions[2]])
    for _ in range(3):
        move_servo([last_positions[0], 150, last_positions[2]])
        move_servo([last_positions[0], 180, last_positions[2]])
    reset_arms_sequentially()


def fist_bump_gesture():
    global last_positions, switch_video
    print("Gesture: Fist Bump")

    # 1. 주먹 내밀기
    move_servo([last_positions[0], 90, last_positions[2]])
    sleep(3)  # 대기

    # 2. 비디오 전환 신호
    switch_video = True

    # 3. 콩콩콩
    for _ in range(4):
        move_servo([10, 130, 80])
        sleep(0.2)
        move_servo([50, 170, 100])
        sleep(0.2)
    reset_arms_sequentially()


def sad_happy_gesture():
    print("Gesture: Sad/Happy")
    for _ in range(3):
        move_servo([100, 0, last_positions[2]], delay=0.02)
        move_servo([180, 80, last_positions[2]], delay=0.02)
    reset_arms_sequentially()


def sleep_gesture():
    print("Gesture: Sleep")
    move_servo([150, 0, last_positions[2]], delay=0.05)
    move_servo([180, 30, last_positions[2]], delay=0.05)


# ========================= Video Functions (User Style) ==============================

def get_video_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    path1 = os.path.join(base_path, '..', 'Resources', filename)
    path2 = os.path.join(base_path, 'Resources', filename)
    if os.path.exists(path1): return path1
    if os.path.exists(path2): return path2
    return filename


def play_video(video_path):
    global stop_video_event
    stop_video_event.clear()

    full_path = get_video_path(video_path)
    cap = cv2.VideoCapture(full_path)

    cv2.namedWindow('Full Screen', cv2.WINDOW_NORMAL)
    # [윈도우 창 위치] 보조모니터면 1920, 아니면 0
    cv2.moveWindow('Full Screen', 1920, 0)
    cv2.setWindowProperty('Full Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        if stop_video_event.is_set(): break

        ret, frame = cap.read()
        if not ret: break

        frame = cv2.resize(frame, (1920, 1080))
        cv2.imshow('Full Screen', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


def play_video_inf(video_path):
    global stop_video_event
    stop_video_event.clear()

    full_path = get_video_path(video_path)
    cap = cv2.VideoCapture(full_path)

    cv2.namedWindow('Full Screen', cv2.WINDOW_NORMAL)
    cv2.moveWindow('Full Screen', 1920, 0)
    cv2.setWindowProperty('Full Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        if stop_video_event.is_set(): break
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (1920, 1080))
            cv2.imshow('Full Screen', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()


def play_video_multiple(first_video, second_video):
    global switch_video

    path1 = get_video_path(first_video)
    path2 = get_video_path(second_video)

    cap = cv2.VideoCapture(path1)

    cv2.namedWindow('Full Screen', cv2.WINDOW_NORMAL)
    cv2.moveWindow('Full Screen', 1920, 0)
    cv2.setWindowProperty('Full Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        if switch_video:
            cap.release()
            cap = cv2.VideoCapture(path2)
            switch_video = False

        ret, frame = cap.read()
        if not ret: break

        frame = cv2.resize(frame, (1920, 1080))
        cv2.imshow('Full Screen', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


# -------------------- Thread Helper --------------------
def ai_to_speech(user_input):
    ai_response = ai_model_response(user_input)
    print(f"🤖 AI Response: {ai_response}")
    text_to_speech(ai_response)


# ====================== MAIN PROGRAM ==========================

if __name__ == "__main__":
    casual_rest()
    pygame.init()

    print("🤖 Nova Started (Windows Free Version)")

    # 초기 인사 및 비디오
    speech_thread = threading.Thread(target=text_to_speech, args=("안녕하세요. 저는 노바입니다.",))
    video_thread = threading.Thread(target=play_video, args=('Casual Eyes.mp4',))

    video_thread.start()
    speech_thread.start()

    while True:
        if video_thread and not video_thread.is_alive():
            video_thread = threading.Thread(target=play_video_inf, args=('Casual Eyes.mp4',))
            video_thread.start()

        user_input = speech_to_text()

        if user_input:
            if video_thread and video_thread.is_alive():
                stop_video_event.set()
                video_thread.join()

            if "안녕" in user_input or "반가워" in user_input:
                video_thread = threading.Thread(target=play_video, args=('Casual Eyes.mp4',))
                gesture_thread = threading.Thread(target=hello_gesture)
                speech_thread = threading.Thread(target=text_to_speech, args=("안녕하세요! 만나서 반가워요.",))

                video_thread.start()
                gesture_thread.start()
                speech_thread.start()

            elif "주먹" in user_input and "인사" in user_input:
                print("Fist bump triggered")
                gesture_thread = threading.Thread(target=fist_bump_gesture)
                video_thread = threading.Thread(target=play_video_multiple, args=("Casual Eyes.mp4", 'Happy Eyes.mp4'))
                speech_thread = threading.Thread(target=text_to_speech, args=("오예! 주먹 인사!",))

                gesture_thread.start()
                video_thread.start()
                speech_thread.start()

            elif "슬퍼" in user_input or "우울" in user_input:
                gesture_thread = threading.Thread(target=sad_happy_gesture)
                video_thread = threading.Thread(target=play_video, args=("Sad Eyes.mp4",))
                speech_thread = threading.Thread(target=text_to_speech, args=("저런.. 너무 슬퍼하지 마세요.",))
                response_thread = threading.Thread(target=ai_to_speech, args=(user_input,))

                gesture_thread.start()
                video_thread.start()
                speech_thread.start()
                # response_thread.start()

            elif "잘자" in user_input or "종료" in user_input:
                print("Sleep mode activated")
                gesture_thread = threading.Thread(target=sleep_gesture)
                video_thread = threading.Thread(target=play_video, args=("Sleepy Eyes.mp4",))
                speech_thread = threading.Thread(target=text_to_speech, args=("네, 안녕히 주무세요.",))

                gesture_thread.start()
                video_thread.start()
                speech_thread.start()
                gesture_thread.join()
                break

            else:
                video_thread = threading.Thread(target=play_video_inf, args=('Casual Eyes.mp4',))
                video_thread.start()

                ai_response = ai_model_response(user_input)
                print(f"AI: {ai_response}")
                text_to_speech(ai_response)