import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

# Initialize components
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set

detector = FaceDetector(minDetectionCon=0.6)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 0)


    img, bboxs = detector.findFaces(img)

    if bboxs:
        for bbox in bboxs:
            x, y, w, h = bbox['bbox']
            # Draw bounding box
            cvzone.cornerRect(img, (x, y, w, h), l=20)
    else:
        print("No face detected.")

    # Display the video feed
    cv2.imshow("Face Detection", img)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
