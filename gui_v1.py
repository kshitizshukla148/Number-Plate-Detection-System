import tkinter as tk
from data import save_to_excel
from ocr_reader import read_plate
from tkinter import filedialog
from PIL import Image, ImageTk
from database import check_vehicle
import os
from datetime import datetime
import cv2

from ultralytics import YOLO
import numpy as np
from openpyxl import Workbook, load_workbook
import os

last_logged_plate = ""


# Load model
model = YOLO("models/best.pt")



# Create window
root = tk.Tk()
root.title("Number Plate Detection System")
root.geometry("900x600")
root.configure(bg="#1e1e1e")  # dark theme

# ---------- TITLE ----------
title = tk.Label(root,
                 text="🚓 ANPR Surveillance System",
                 font=("Arial", 22, "bold"),
                 bg="#1e1e1e",
                 fg="#00ffcc")
title.pack(pady=10)

# ---------- FRAME (IMAGE + RESULT) ----------
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack()

# Image display label
image_label = tk.Label(main_frame, bg="#1e1e1e")
image_label.grid(row=0, column=0, padx=20)


# RESULT PANEL
result_frame = tk.Frame(main_frame, bg="#2c2c2c", width=300, height=400)
result_frame.grid(row=0, column=1, padx=20)

result_title = tk.Label(result_frame,
                        text="Detection Result",
                        font=("Arial", 16, "bold"),
                        bg="#2c2c2c",
                        fg="white")
result_title.pack(pady=10)

result_label = tk.Label(result_frame,
                        text="Plate Number: ---",
                        font=("Arial", 14),
                        bg="#2c2c2c",
                        fg="#00ff00")
result_label.pack(pady=20)

status_label = tk.Label(result_frame,
                        text="Status: Waiting...",
                        font=("Arial", 12),
                        bg="#2c2c2c",
                        fg="yellow")
status_label.pack(pady=10)


def detect_plate():

    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files","*.jpg *.png *.jpeg")]
    )

    if not file_path:
        return

    img = cv2.imread(file_path)

    results = model(img)

    plate_text = ""

    for r in results:

        boxes = r.boxes.xyxy

        for box in boxes:

            x1,y1,x2,y2 = map(int,box)

            pad = 10
            plate_img = img[y1-pad:y2+pad, x1-pad:x2+pad]

            # OCR
            plate_text = read_plate(plate_img)
            
            global last_logged_plate

            if plate_text and plate_text != last_logged_plate:

                is_criminal = check_vehicle(plate_text)

                if is_criminal:
                    save_to_excel(plate_text, "CRIMINAL")
                    status_label.config(
                    text="Status: CRIMINAL DETECTED 🚨",
                    fg="red"
                )
                else:
                    save_to_excel(plate_text, "SAFE")
                    status_label.config(
                    text="Status: SAFE VEHICLE",
                    fg="green"
                )

                last_logged_plate = plate_text

           
                if is_criminal:
                        result_label.config(
                            text=f"⚠ CRIMINAL VEHICLE: {plate_text}",
                            fg="red"
                        )
                else:
                        result_label.config(
                            text=f"Plate Number: {plate_text}",
                            fg="green"
                        )
                            
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)

    # Convert image for Tkinter
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil = img_pil.resize((700,400))

    img_tk = ImageTk.PhotoImage(img_pil)

    image_label.config(image=img_tk)
    image_label.image = img_tk

    if plate_text != "":
        result_label.config(text=f"Plate Number: {plate_text}")
    else:
        result_label.config(text="Plate Number: Not Detected")
        


def save_criminal_image(frame, plate):

    # create folder if not exists
    folder = "criminal_captures"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{folder}/{plate}_{timestamp}.jpg"

    cv2.imwrite(filename, frame)

    print(f"⚠ Criminal vehicle saved: {filename}")
    
    

def detect_video():

    file_path = filedialog.askopenfilename(
        filetypes=[("Video Files","*.mp4 *.avi *.mov")]
    )

    if not file_path:
        return

    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        print("Error opening video")
        return
    
    
    frame_count = 0

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % 5 != 0:
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

    

        results = model(frame)

        for r in results:

            boxes = r.boxes.xyxy

            for box in boxes:

                x1,y1,x2,y2 = map(int,box)

                pad = 10
                plate_img = frame[y1:y2, x1:x2]

                plate_text = read_plate(plate_img)
                
                global last_logged_plate

                if plate_text and plate_text != last_logged_plate:

                    plate_text = read_plate(plate_img)

                    # ✅ Only proceed if valid plate
                    if plate_text:

                        # check criminal
                        if check_vehicle(plate_text):

                            cv2.putText(frame, f"CRIMINAL: {plate_text}", (x1,y1-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

                            save_criminal_image(frame, plate_text)

                            # ✅ save only here
                            save_to_excel(plate_text, "CRIMINAL")

                        else:

                            cv2.putText(frame, plate_text, (x1,y1-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                            # ✅ save only valid plates
                            save_to_excel(plate_text, "SAFE")

                    last_logged_plate = plate_text

                    

                else:

                        cv2.putText(frame,
                                    plate_text,
                                    (x1,y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (0,255,0),
                                    2)

                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

        cv2.imshow("Video Detection", frame)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def start_camera():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not found")
        return

    def update_frame():

        global last_logged_plate

        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            return

        results = model(frame, verbose=False)

        for r in results:

            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:

                x1,y1,x2,y2 = map(int,box)

                h, w, _ = frame.shape

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                plate_img = frame[y1:y2, x1:x2]

                plate_text = read_plate(plate_img)

                if plate_text and 6 <= len(plate_text) <= 12:

                    is_criminal = check_vehicle(plate_text)

                    if is_criminal:

                        # 🚨 CRIMINAL (in database)
                        cv2.putText(frame,
                                    f"CRIMINAL: {plate_text}",
                                    (x1,y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (0,0,255),
                                    2)

                        result_label.config(
                            text=f"⚠ CRIMINAL: {plate_text}",
                            fg="red"
                        )

                        save_criminal_image(frame, plate_text)
                        save_to_excel(plate_text, "CRIMINAL")

                    else:

                        # ✅ SAFE (not in database)
                        cv2.putText(frame,
                                    plate_text,
                                    (x1,y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (0,255,0),
                                    2)

                        result_label.config(
                            text=f"SAFE: {plate_text}",
                            fg="green"
                        )

                        save_to_excel(plate_text, "SAFE")

        # Convert frame for Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_pil = img_pil.resize((700,400))

        img_tk = ImageTk.PhotoImage(img_pil)

        image_label.config(image=img_tk)
        image_label.image = img_tk

        root.after(10, update_frame)
    update_frame()

# ---------- BUTTON FRAME ----------
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=20)

def style_button(btn):
    btn.config(
        font=("Arial", 13, "bold"),
        bg="#333",
        fg="white",
        activebackground="#00ffcc",
        activeforeground="black",
        width=25,
        height=2,
        bd=0
    )

# Buttons
btn1 = tk.Button(btn_frame, text="📂 Detect from Image", command=detect_plate)
style_button(btn1)
btn1.grid(row=0, column=0, padx=10, pady=10)

btn2 = tk.Button(btn_frame, text="🎥 Video Detection", command=detect_video)
style_button(btn2)
btn2.grid(row=0, column=1, padx=10, pady=10)

btn3 = tk.Button(btn_frame, text="📷 Live Camera", command=start_camera)
style_button(btn3)
btn3.grid(row=0, column=2, padx=10, pady=10)

# ---------- FOOTER ----------
footer = tk.Label(root,
                  text="Developed by Kshitiz Shukla",
                  bg="#1e1e1e",
                  fg="gray",
                  font=("Arial", 10))
footer.pack(side="bottom", pady=10)

root.mainloop()