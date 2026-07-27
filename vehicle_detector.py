from ultralytics import YOLO
import cv2
import subprocess
import time
import sys

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera could not be opened")
    exit()
last_scan = 0
cooldown = 5  # seconds

print("AI Vehicle Detector Started")
print("Press Q to Quit")

while True:

    success, frame = cap.read()

    if not success:
        break

    results = model(frame, verbose=False)

    vehicle_found = False

    for r in results:

        for box in r.boxes:

            cls = int(box.cls[0])
            name = model.names[cls]

            if name in ["car", "truck", "bus", "motorcycle"]:

                vehicle_found = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 255, 0), 2)

                cv2.putText(frame,
                            name,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2)

    if vehicle_found and (time.time() - last_scan > cooldown):

        print("Vehicle Detected")
        print("Capturing Image...")

        cv2.imwrite("test.jpg", frame)

        subprocess.run([sys.executable, "ocr_reader.py"])

        last_scan = time.time()

    cv2.imshow("AI Vehicle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()