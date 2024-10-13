import streamlit as st
import qrcode
import sqlite3
import io
import random
import string
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
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
if run:
    cap = cv2.VideoCapture(0)

while run:
    ret, frame = cap.read()

    if not ret:
        st.error("Failed to grab frame")
        break

    # Convert the frame to RGB for display in Streamlit
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame)

    st.session_state[qr_code_data]=False
    # Decode the QR code in the frame
    decoded_objects = decode(frame)
    if decoded_objects:
        for obj in decoded_objects:
            qr_code_data = obj.data.decode('utf-8')
            st.write(f"QR Code detected: {qr_code_data}")

            if mark_attendance(qr_code_data) and st.session_state[qr_code_data]==False:
                st.success(f"Attendance marked for QR code: {qr_code_data}")
                st.session_state[qr_code_data]=True
            elif st.session_state[qr_code_data]==True:
                st.error(f"QR Code not recognized")
                st.session_state[qr_code_data]=False

    # Stop when the checkbox is unchecked
    if not run:
        break

if cap:
    cap.release()
    cv2.destroyAllWindows()