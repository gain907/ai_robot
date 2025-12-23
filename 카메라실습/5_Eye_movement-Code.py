import cv2
from cvzone.FaceDetectionModule import FaceDetector
from cvzone.PIDModule import PID

# Load images
background_img = cv2.imread('../Resources/Eye-Background.png', cv2.IMREAD_UNCHANGED)
iris_img = cv2.imread('../Resources/Eye-Ball.png', cv2.IMREAD_UNCHANGED)

# 웹캠 초기화 (0번은 내장 캠, 외장은 1, 2번)
cap = cv2.VideoCapture(0)
# 화면 해상도 설정
cap.set(3, 640)  # 가로(Width) 설정
cap.set(4, 480)  # 세로(Height) 설정


# minDetectionCon=0.6: 정확도가 60% 이상일 때만 얼굴로 인식
detector = FaceDetector(minDetectionCon=0.6)
# 4. PID 제어기 초기화 (X축 제어용)
# [0.015, 0, 0.06]: PID 계수 (Kp, Ki, Kd) - 반응 속도와 부드러움을 조절하는 값
# 640 // 2: 목표값(Target) - 화면의 정중앙인 320 좌표를 목표로 함
# axis=0: X축(가로) 기준으로 제어
xPID = PID([0.015, 0, 0.06], 640 // 2, axis=0)


# Function to overlay the iris on the background
def overlay_iris(background, iris, x, y):
    h, w = iris.shape[:2]
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        iris = iris[:, :w]
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        iris = iris[:h]

    alpha = iris[:, :, 3] / 255.0
    for c in range(3):
        background[y:y+h, x:x+w, c] = alpha * iris[:, :, c] + (1 - alpha) * background[y:y+h, x:x+w, c]

# Initialize iris position in the center
iris_position = (325, 225)  # (x, y)

# Create a named window and set it to full screen
cv2.namedWindow('Overlay Result', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Overlay Result', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 0)
    cv2.imshow("Webcam", img)

    img, bboxs = detector.findFaces(img)

    if bboxs:
        cx = bboxs[0]['center'][0]
        resultX = int(xPID.update(cx))
        print(resultX)

        # Update iris position based on resultX
        if resultX > 1:
            iris_position = (400, 225)  # Move iris to the right
        elif resultX < -1:
            iris_position = (250, 225)  # Move iris to the left
        else:
            iris_position = (325,225)  # Center iris

    print(iris_position)

    # Overlay the iris on the background image
    background_with_iris = background_img.copy()
    overlay_iris(background_with_iris, iris_img, iris_position[0], iris_position[1])

    # Display results and move the window
    cv2.imshow('Overlay Result', background_with_iris)
    # cv2.moveWindow("Overlay Result", 1792, 100)
    cv2.moveWindow('Overlay Result', 1920, 0)

    # Wait until a key is pressed to close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
