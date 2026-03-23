import cv2
import os
import datetime
from detector import detect_plate
from ocr_reader import read_plate
from database import check_vehicle

os.makedirs("output/screenshots", exist_ok=True)
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

frame_count = 0

while True:

    ret, frame = cap.read()
    if not ret:
        break

    plates = detect_plate(frame)

    for (x1, y1, x2, y2) in plates:

        plate_img = frame[y1:y2, x1:x2]

        text = read_plate(plate_img)

        if text != "":

            if check_vehicle(text):
                color = (0,0,255)
                label = "CRIMINAL: " + text

                filename = "output/screenshots/" + text + ".jpg"
                cv2.imwrite(filename, frame)

            else:
                color = (0,255,0)
                label = text

            cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
            cv2.putText(frame,label,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,color,2)

    cv2.imshow("Vehicle Surveillance System",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()