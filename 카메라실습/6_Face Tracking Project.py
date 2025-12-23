# ---------------------------------------------------------
# [Windows Version] Face Tracking Robot
# ---------------------------------------------------------
import cv2
from cvzone.FaceDetectionModule import FaceDetector
from cvzone.PIDModule import PID
from cvzone.SerialModule import SerialObject
import os
from time import sleep

# 1. 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
resource_path = os.path.join(current_dir, '..', 'Resources')
bg_file_path = os.path.join(resource_path, 'Eye-Background.png')
iris_file_path = os.path.join(resource_path, 'Eye-Ball.png')

background_img = cv2.imread(bg_file_path, cv2.IMREAD_UNCHANGED)
iris_img = cv2.imread(iris_file_path, cv2.IMREAD_UNCHANGED)

if background_img is None or iris_img is None:
    print("!! 이미지 로드 실패: 경로를 확인하세요 !!")
    exit()

# 2. 카메라 설정 (윈도우는 요청한 해상도로 잘 열림)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = FaceDetector(minDetectionCon=0.6)
# 윈도우는 해상도가 고정되므로 중앙값(320)을 고정해도 잘 작동함
xPID = PID([0.03, 0, 0.06], 640 // 2, axis=0)
xAngle = 105

# 3. 아두이노 연결
print("Arduino Connecting...")
try:
    arduino = SerialObject(digits=3)
    sleep(2.5)  # 부팅 대기
    print("Arduino Connected!")
    arduino.sendData([180, 0, 105])  # 초기 위치 전송
except:
    print("!! 아두이노 연결 실패 !!")
    arduino = None

center_threshold = 2


def overlay_iris(background, iris, x, y):
    h, w = iris.shape[:2]
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        iris = iris[:, :w]
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        iris = iris[:h]
    if h <= 0 or w <= 0: return

    if iris.shape[2] == 4:
        alpha = iris[:, :, 3] / 255.0
        for c in range(3):
            background[y:y + h, x:x + w, c] = alpha * iris[:, :, c] + (1 - alpha) * background[y:y + h, x:x + w, c]
    else:
        background[y:y + h, x:x + w] = iris


# 4. 윈도우 창 설정 (전체 화면 강제 적용)
cv2.namedWindow('Overlay Result', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Overlay Result', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

iris_position = (325, 225)

while True:
    success, img = cap.read()
    if not success: break

    img = cv2.flip(img, 0)  # 카메라 방향에 따라 0 또는 1 설정
    img, bboxs = detector.findFaces(img)

    if bboxs:
        cx = bboxs[0]['center'][0]
        resultX = int(xPID.update(cx))

        # 눈동자 그래픽 이동
        if resultX > 5:
            iris_position = (400, 225)
        elif resultX < -5:
            iris_position = (250, 225)
        else:
            iris_position = (325, 225)

        # 모터 제어
        if abs(resultX) > center_threshold:
            xAngle += resultX  # 방향 반대면 -= 로 수정

        # 각도 안전장치 (Clamping)
        if xAngle > 180: xAngle = 180
        if xAngle < 0: xAngle = 0

        if arduino:
            arduino.sendData([180, 0, xAngle])

    background_with_iris = background_img.copy()
    overlay_iris(background_with_iris, iris_img, iris_position[0], iris_position[1])

    # 윈도우용: 디버깅창(img)도 띄우고 결과창도 띄움
    cv2.imshow("Webcam", img)
    cv2.imshow('Overlay Result', background_with_iris)

    # 듀얼 모니터일 경우 이동 (필요 시 주석 해제)
    # cv2.moveWindow('Overlay Result', 1920, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()