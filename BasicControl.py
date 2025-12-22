from cvzone.SerialModule import SerialObject

# ------------------- Configurations -------------------

# 아두이노 시리얼 통신 초기화 (포트 번호는 필요하면 "COM3" 등으로 입력)
arduino = SerialObject(digits=3)

# [수정됨] 초기 상태: 릴레이(전구) 값을 빼고 3개로 줄였습니다.
# [Motor1(Left Hand), Motor2(Right Hand), Motor3(Head)]
state = [180, 0, 90]


# ------------------- Main Program -------------------

def update_state(action_number):
    global state

    if action_number == "0":  # 모든 모터 초기 위치로 리셋 (Reset)
        state = [180, 0, 90]

    elif action_number == "1":  # 왼쪽 팔을 90도로 이동
        state[0] = 90

    elif action_number == "2":  # 오른쪽 팔을 90도로 이동
        state[1] = 90

    elif action_number == "3":  # 머리를 90도로 이동
        state[2] = 90

    # (4번, 5번은 전구 기능이었으므로 삭제했습니다)

    elif action_number == "4":  # 모든 모터를 90도로 이동 (전구 켜기 기능 삭제됨)
        state = [90, 90, 90]

    # [중요] 아두이노로 데이터 전송 (이제 3개의 값만 보냅니다)
    arduino.sendData(state)


# ------------------- User Input -------------------

while True:
    # 전구 관련 번호(4, 5)는 제외하고 안내합니다.
    user_input = input("작동할 번호를 입력하세요 (0, 1, 2, 3, 4): ")

    if user_input in ["0", "1", "2", "3", "4"]:
        update_state(user_input)
    else:
        print("잘못된 입력입니다. 0, 1, 2, 3, 4 중에서 입력해 주세요.")