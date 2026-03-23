from ultralytics import YOLO
import cv2
import os

model = YOLO("models/best.pt")

folder = "images"

total = 0
detected = 0

for img_name in os.listdir(folder):

    path = os.path.join(folder, img_name)
    
    results = model(path, save=True)

    print(img_name, "processed")

    img = cv2.imread(path)

    results = model(img)

    boxes = results[0].boxes

    total += 1

    if len(boxes) > 0:
        detected += 1
        print(img_name, "→ Plate detected")
    else:
        print(img_name, "→ No detection")

print("\nTotal images:", total)
print("Detected plates:", detected)

accuracy = (detected / total) * 100
print("Detection accuracy:", accuracy,"%")