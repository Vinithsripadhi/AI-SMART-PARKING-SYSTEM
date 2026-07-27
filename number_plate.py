import cv2
import easyocr
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# OCR Reader
reader = easyocr.Reader(['en'])

# Open Webcam
cap = cv2.VideoCapture(0)

# Vehicle class IDs in COCO
vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame)

    for result in results:

        boxes = result.boxes

        for box in boxes:

            cls = int(box.cls[0])

            if cls in vehicle_classes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw vehicle box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                vehicle = frame[y1:y2, x1:x2]

                # OCR
                text = reader.readtext(vehicle)

                for t in text:

                    plate = t[1]

                    if len(plate) >= 6:

                        cv2.putText(
                            frame,
                            plate,
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (255,0,0),
                            2
                        )

                        print("Detected Plate:", plate)

    cv2.imshow("Number Plate Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()