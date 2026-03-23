from ultralytics import YOLO
import cv2

model = YOLO("models/best.pt")

img = cv2.imread("images/car.jpg")

cv2.waitKey(1)
results = model(img, show=True)