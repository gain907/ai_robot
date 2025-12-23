import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector
from cvzone.PIDModule import PID
from cvzone.PlotModule import LivePlot

# Constants
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
X_CENTER = FRAME_WIDTH // 2
SERVO_MAX = 180
SERVO_MIN = 0
INITIAL_X_ANGLE = 105

# Initialize components
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)  # Set width
cap.set(4, FRAME_HEIGHT)  # Set height
detector = FaceDetector(minDetectionCon=0.75)
xPID = PID([0.015, 0, 0.06], X_CENTER, axis=0)
xPlot = LivePlot(yLimit=[0, FRAME_WIDTH], char="X")
xAngle = INITIAL_X_ANGLE

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from the camera.")
        break
    # 화면 반전 처리
    img = cv2.flip(img, 0)  # 0: 상하 반전 (카메라가 거꾸로 달려있을 때 사용)
    # img = cv2.flip(img, 1) # 1: 좌우 반전 (거울 모드, 보통 이걸 많이 씀)

    # img = cv2.flip(img, 1)  # Horizontal flip for natural mirroring
    # imgOut = img.copy()
    img, bboxs = detector.findFaces(img)

    if bboxs:
        x, y, w, h = bboxs[0]['bbox']
        cx, cy = bboxs[0]['center']
        resultX = int(xPID.update(cx))
        xAngle = max(SERVO_MIN, min(SERVO_MAX, xAngle + resultX))  # Clamp xAngle
        imgPlotX = xPlot.update(cx)

        img = xPID.draw(img, [cx, cy])
        # 그래프 창 띄우기
        cv2.imshow("Image X plot", imgPlotX)
    else:
        print("No face detected.")


    # Display the main video feed
    cv2.imshow("Image", img)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
