import cv2
# import cvzone # (주석 처리됨)
from cvzone.FaceDetectionModule import FaceDetector
from cvzone.PIDModule import PID

# 1. 웹캠 초기화 (0번은 내장 캠, 외장은 1, 2번)
cap = cv2.VideoCapture(0)

# 2. 화면 해상도 설정 (640x480)
cap.set(3, 640)  # 가로(Width) 설정
cap.set(4, 480)  # 세로(Height) 설정

# 3. 얼굴 인식 모듈 초기화
# minDetectionCon=0.6: 정확도가 60% 이상일 때만 얼굴로 인식
detector = FaceDetector(minDetectionCon=0.6)

# 4. PID 제어기 초기화 (X축 제어용)
# [0.015, 0, 0.06]: PID 계수 (Kp, Ki, Kd) - 반응 속도와 부드러움을 조절하는 값
# 640 // 2: 목표값(Target) - 화면의 정중앙인 320 좌표를 목표로 함
# axis=0: X축(가로) 기준으로 제어
xPID = PID([0.015, 0, 0.06], 640 // 2, axis=0)

# 서보 모터의 초기 각도 설정 (현재는 계산만 하고 모터를 실제로 움직이는 코드는 없음)
xAngle = 105

while True:
    # 5. 프레임 읽어오기
    success, img = cap.read()

    # [추가할 코드] 카메라가 안 켜졌으면 프로그램을 멈춤
    if not success:
        print("카메라를 찾을 수 없습니다! 번호를 확인하거나 연결 상태를 점검하세요.")
        break  # 루프 탈출

    # 6. 화면 반전 처리
    img = cv2.flip(img, 0)  # 0: 상하 반전 (카메라가 거꾸로 달려있을 때 사용)
    # img = cv2.flip(img, 1) # 1: 좌우 반전 (거울 모드, 보통 이걸 많이 씀)

    # 7. 얼굴 찾기 (그리기 기능 포함)
    # img: 얼굴 박스가 그려진 이미지, bboxs: 감지된 얼굴 정보 리스트
    img, bboxs = detector.findFaces(img)

    # 8. 얼굴이 감지되었을 때만 실행
    if bboxs:
        # 첫 번째 감지된 얼굴의 정보 가져오기
        x, y, w, h = bboxs[0]['bbox']  # x, y 좌표 및 너비, 높이
        cx, cy = bboxs[0]['center']  # 얼굴의 중심 좌표 (cx, cy)

        # 9. PID 계산 (핵심 로직)
        # 현재 얼굴 중심(cx)이 화면 중앙(320)과 얼마나 차이나는지 계산하여
        # 모터를 얼마나 움직여야 할지(resultX)를 반환함
        resultX = int(xPID.update(cx))

        # 계산된 값만큼 각도 변경 (추적)
        xAngle += resultX

        # 디버깅용 출력: 모터가 움직여야 할 값
        print(resultX)

        # 10. PID 그래프 그리기 (화면에 목표치와 현재 위치 차이를 시각적으로 보여줌)
        img = xPID.draw(img, [cx, cy])

    # 11. 결과 화면 출력
    cv2.imshow("Image", img)

    # 12. 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제 및 창 닫기
cap.release()
cv2.destroyAllWindows()

# xPID = PID([0.015, 0, 0.06], 640 // 2, axis=0)
# 목표(SetPoint): 640 // 2 = 320. 즉, 화면의 가로 중앙입니다.
# 입력(Process Variable): cx. 현재 내 얼굴의 X 좌표입니다.
# 오차(Error): 목표(320) - 현재위치(cx). 얼굴이 중앙에서 얼마나 벗어났는지입니다.
# PID 계수 [0.015, 0, 0.06]의 의미:
# P (Proportional, 비례): 0.015. 오차가 클수록(멀리 있을수록) 더 빨리 움직이게 합니다.
# I (Integral, 적분): 0. 누적 오차를 보정하지만, 여기선 사용하지 않았습니다.
# D (Derivative, 미분): 0.06. 급브레이크 역할입니다. 목표에 가까워질수록 속도를 줄여서 덜덜 떨지 않고 부드럽게 멈추게 합니다.