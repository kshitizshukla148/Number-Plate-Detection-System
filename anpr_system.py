import cv2
from ultralytics import YOLO
import easyocr
import os
import datetime

# Load YOLO model
model = YOLO("yolov8n.pt")

# OCR Reader
reader = easyocr.Reader(['en'])

# Criminal vehicle database
criminal_db = ["UP32AB1234", "HR26DK8337"]

# Create screenshot folder
os.makedirs("output/screenshots", exist_ok=True)

# Start camera
cap = cv2.VideoCapture(0)

frame_count = 0

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Run detection every 5 frames (speed improvement)
    if frame_count % 5 == 0:

        results = model(frame)

        for r in results:

            for box in r.boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                plate = frame[y1:y2, x1:x2]

                if plate.size == 0:
                    continue

                # OCR
                ocr_result = reader.readtext(plate)

                for detection in ocr_result:

                    plate_text = detection[1].replace(" ", "").upper()

                    if plate_text == "":
                        continue

                    print("Detected:", plate_text)

                    # Check criminal database
                    if plate_text in criminal_db:

                        color = (0,0,255)
                        label = "CRIMINAL: " + plate_text

                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                        filename = f"output/screenshots/{plate_text}_{timestamp}.jpg"

                        cv2.imwrite(filename, frame)

                    else:

                        color = (0,255,0)
                        label = plate_text

                    # Draw box
                    cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)

                    cv2.putText(frame,label,(x1,y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,color,2)

    cv2.imshow("ANPR System",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()