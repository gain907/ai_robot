"""
Basic Servo Movement Script for Talking AI Robot
- Uses cvzone to communicate with Arduino
- Controls 3 Servos: Left Arm, Right Arm, Head
"""
# ------------------- 1. 라이브러리 불러오기 -------------------
from cvzone.SerialModule import SerialObject  # 아두이노와 통신하기 위한 도구
from time import sleep  # 시간 지연을 위한 도구
# ------------------- 2. 초기 설정 및 연결 -------------------
# 아두이노와 연결 설정 (digits=3은 90도를 090으로 보내는 설정)
# 주의: 실제로 연결된 포트를 자동으로 찾지만, 만약 안 되면 포트를 직접 적어줘야 할 수도 있습니다. 예: port='COM3'
arduino = SerialObject(digits=3)

# ★★★ [중요] 아두이노 부팅 대기 ★★★
# 아두이노가 시리얼 연결 후 재부팅되는 시간을 벌어줍니다.
print("Arduino Connecting...")
sleep(2.5)
print("Ready to move!")

# 서보모터의 현재 위치를 기억하는 리스트 (초기값 설정)
# 순서: [왼팔(LServo), 오른팔(RServo), 머리(HServo)]
# 초기 상태: 왼팔은 들고(180), 오른팔은 내리고(0), 머리는 정면(90)
last_positions = [180, 0, 90]


# ------------------- 3. 함수 정의 (움직임 로직) -------------------

def move_servo(target_positions, delay=0.0001):
    """
    서보모터를 현재 위치에서 목표 위치까지 부드럽게 이동시키는 함수
    :param target_positions: 목표 각도 리스트 [왼팔, 오른팔, 머리]
    :param delay: 움직임 사이의 대기 시간 (값이 클수록 느리게 움직임)
    """
    global last_positions  # 밖에 있는 위치 변수를 가져와서 갱신함

    # 각 모터별로 이동해야 할 거리를 계산해서 가장 먼 거리를 기준으로 단계(step)를 정함
    max_steps = max(abs(target_positions[i] - last_positions[i]) for i in range(3))

    # 계산된 단계만큼 조금씩 나누어 이동 (부드러운 움직임 구현)
    for step in range(max_steps):
        current_positions = []
        for i in range(3):
            # 시작점과 목표점 사이를 step만큼 쪼개서 중간 각도를 계산하는 공식
            if abs(target_positions[i] - last_positions[i]) > step:
                move_amount = (step + 1) * (target_positions[i] - last_positions[i]) // max_steps
                current_positions.append(last_positions[i] + move_amount)
            else:
                current_positions.append(last_positions[i])

        # 계산된 중간 각도를 아두이노로 전송
        arduino.sendData(current_positions)
        sleep(delay)  # 너무 빠르지 않게 미세하게 대기

    # 이동이 끝났으므로 목표 위치를 현재 위치로 저장
    last_positions = target_positions[:]


def hello_gesture():
    """
    오른팔을 들어 흔들며 인사하는 동작
    """
    global last_positions
    print("Action: Hello Gesture Start")

    # 1. 인사 준비: 오른팔을 180도로 들어 올림
    move_servo([last_positions[0], 180, last_positions[2]])

    # 2. 손 흔들기: 3번 반복
    for _ in range(3):
        move_servo([last_positions[0], 150, last_positions[2]])  # 살짝 내림
        move_servo([last_positions[0], 180, last_positions[2]])  # 다시 올림

    # 3. 제자리: 오른팔을 천천히 내림 (delay를 늘려서 우아하게)
    move_servo([last_positions[0], 0, last_positions[2]], delay=0.015)
    print("Action: Hello Gesture Finished")


# ------------------- 4. 메인 실행 (Main Loop) -------------------

if __name__ == "__main__":
    # 스크립트가 실행되면 바로 인사 동작을 수행합니다.
    try:
        hello_gesture()
    except KeyboardInterrupt:
        print("Program stopped by User")
