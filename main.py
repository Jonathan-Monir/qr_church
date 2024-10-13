import streamlit as st
import qrcode
import sqlite3
import io
import random
import string
from PIL import Image
import imageio
import numpy as np
import cv2  # For QR code decoding and video capture
from datetime import date

# Function to mark attendance
def mark_attendance(qr_code):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    # Check if the student exists
    c.execute("SELECT id FROM students WHERE qr_code = ?", (qr_code,))
    result = c.fetchone()

    if result:
        student_id = result[0]
        today = date.today().isoformat()

        # Create the attendance table for storing attendance records if not exists
        c.execute(f'''CREATE TABLE IF NOT EXISTS attendance_log (
                        student_id INTEGER,
                        attendance_date DATE,
                        attended INTEGER,
                        PRIMARY KEY (student_id, attendance_date),
                        FOREIGN KEY(student_id) REFERENCES attendance(id)
                     )''')

        # Mark the student as attended for today
        c.execute(f"INSERT OR IGNORE INTO attendance_log (student_id, attendance_date, attended) VALUES (?, ?, ?)",
                  (student_id, today, 1))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

# Streamlit app interface
st.title("Student Attendance QR Code Generator and Scanner")

# QR Code scanning page
st.write("Scan a QR Code to mark attendance")

# Open the webcam
run = st.checkbox("Start Camera")

FRAME_WINDOW = st.image([])

cap = None
qr_decoder = cv2.QRCodeDetector()  # Initialize QRCodeDetector

# Initialize session state to track processed QR codes
if "processed_qr_codes" not in st.session_state:
    st.session_state.processed_qr_codes = set()

if run:
    # Start the webcam capture using OpenCV
    cap = cv2.VideoCapture(0)  # 0 is the default camera

while run:
    if cap.isOpened():
        ret, frame = cap.read()  # Capture frame-by-frame
        if not ret:
            st.error("Failed to capture video frame")
            break

        # Convert the frame to RGB for display in Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame_rgb)

        # Decode the QR code in the frame using OpenCV
        qr_code_data, points, _ = qr_decoder.detectAndDecode(frame)

        if qr_code_data:
            # Check if the QR code has already been processed
            if qr_code_data not in st.session_state.processed_qr_codes:
                if mark_attendance(qr_code_data):
                    st.success(f"Attendance marked for QR code: {qr_code_data}")
                    st.session_state.processed_qr_codes.add(qr_code_data)
                else:
                    st.warning(f"QR code not recognized: {qr_code_data}")
            else:
                st.info(f"QR code {qr_code_data} has already been processed")

    else:
        st.error("Webcam not found or cannot be opened")

    # Stop when the checkbox is unchecked
    if not run:
        cap.release()
        break
