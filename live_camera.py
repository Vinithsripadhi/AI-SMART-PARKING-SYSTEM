import cv2
import subprocess

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera")
    exit()

print("Press S to capture")
print("Press Q to quit")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("Smart Parking Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):

        cv2.imwrite("test.jpg", frame)

        print("Image Saved")
        print("Running OCR...")

        subprocess.run(["python", "ocr_reader.py"])

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()