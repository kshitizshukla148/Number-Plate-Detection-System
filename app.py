import streamlit as st
import numpy as np
import cv2

import datetime
import os
from detector import detect_plate
from ocr_reader import read_plate
from database import check_vehicle

st.set_page_config(page_title="Vehicle Surveillance System", layout="wide")

st.title("🚗 AI Vehicle Surveillance Dashboard")

menu = st.sidebar.selectbox(
    "Select Mode",
    ["Live Camera", "Upload Image", "Detection History"]
)

os.makedirs("output/screenshots", exist_ok=True)

# ---------------- LIVE CAMERA ----------------

if menu == "Live Camera":

    st.header("📹 Live Camera Detection")

    start = st.button("Start Camera")

    frame_window = st.image([])

    if start:

        cap = cv2.VideoCapture(0)
        cap.set(3,1280)
        cap.set(4,720)

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

                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                        filename = f"output/screenshots/{text}_{timestamp}.jpg"

                        cv2.imwrite(filename, frame)

                        st.error(f"🚨 Criminal Vehicle Detected: {text}")

                    else:
                        color = (0,255,0)
                        label = text

                    cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)

                    cv2.putText(frame,label,(x1,y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,color,2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_window.image(frame)

# ---------------- IMAGE UPLOAD ----------------


elif menu == "Upload Image":

    st.header("📷 Detect Plate from Image")

    uploaded_file = st.file_uploader("Upload vehicle image", type=["jpg","png","jpeg"])

    if uploaded_file is not None:

        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Resize image (helps YOLO detection)
        image = cv2.resize(image, (1280,720))

        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Uploaded Image")

        plates = detect_plate(image)

        st.write("Detected boxes:", plates)   # DEBUG (remove later)

        detected = False

        for (x1, y1, x2, y2) in plates:

            plate_img = image[y1:y2, x1:x2]

            text = read_plate(plate_img)

            if text != "":

                detected = True

                if check_vehicle(text):
                    st.error(f"🚨 Criminal Vehicle Detected: {text}")
                    color = (0,0,255)

                else:
                    st.success(f"Vehicle Plate: {text}")
                    color = (0,255,0)

                cv2.rectangle(image,(x1,y1),(x2,y2),color,2)

        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Detection Result")

        if not detected:
            st.warning("No number plate detected")

# ---------------- HISTORY ----------------

elif menu == "Detection History":

    st.header("📂 Detection History")

    images = os.listdir("output/screenshots")

    for img in images:

        st.image(f"output/screenshots/{img}", caption=img)