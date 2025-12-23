# ------------------- Import Library -------------------

import cv2

# Initialize the webcam
# Change '0' to the appropriate camera index for an external camera (e.g., '1', '2', etc.)
cap = cv2.VideoCapture(0)
# Set frame width and height# ------------------- Import Library -------------------
#
# import cv2
#
# # Initialize the webcam
# # Change '0' to the appropriate camera index for an external camera (e.g., '1', '2', etc.)
# cap = cv2.VideoCapture(1)
# # Set frame width and height
# cap.set(3, 640)
# cap.set(4, 480)
#
# # ------------------- Main Program -------------------
#
# while True:
#     # Capture frame-by-frame
#     success, img = cap.read()
#
#     # Display the resulting frame
#     cv2.imshow("Image", img)
#
#     # Exit condition: Press 'q' to quit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Release the webcam and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()
cap.set(3, 640)
cap.set(4, 480)

# ------------------- Main Program -------------------

while True:
    # Capture frame-by-frame
    success, img = cap.read()

    # 카메라 프레임을 제대로 읽지 못했다면 루프 종료 (안전장치)
    if not success:
        print("프레임을 읽을 수 없습니다.")
        break

    # [추가된 부분] 이미지를 위아래로 반전시킵니다.
    # 0: 상하 반전 (Vertical Flip)
    # 1: 좌우 반전 (Mirror)
    # -1: 상하좌우 모두 반전
    img = cv2.flip(img, 0)

    # Display the resulting frame
    cv2.imshow("Image", img)

    # Exit condition: Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()