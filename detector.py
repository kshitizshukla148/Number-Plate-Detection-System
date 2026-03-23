from ultralytics import YOLO

# load trained model
model = YOLO("models/best.pt")

def detect_plate(frame):

    # run detection with confidence threshold
    results = model(frame, conf=0.25)

    plates = []

    for result in results:
        boxes = result.boxes

        for box in boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # add small margin (helps OCR)
            pad =20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = x2 + 10
            y2 = y2 + 10

            plates.append((x1, y1, x2, y2))

    return plates