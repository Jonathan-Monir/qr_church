import streamlit as st
import qrcode
import sqlite3
import io
import random
import string
from PIL import Image
import imageio
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
import imageio
from pyzbar.pyzbar import decode  # Assuming you're using pyzbar for QR code decoding

# Initialize session state to track processed QR codes
if "processed_qr_codes" not in st.session_state:
    st.session_state.processed_qr_codes = set()

# Use imageio's get_reader for webcam
if run:
    reader = imageio.get_reader("<video0>")  # "<video0>" corresponds to the first camera

while run:
    try:
        frame = reader.get_next_data()  # Get the next frame

        # Convert the frame to RGB for display in Streamlit
        frame_rgb = frame[..., :3]  # imageio returns a frame in RGBA, keep only RGB
        FRAME_WINDOW.image(frame_rgb)

        # Decode the QR code in the frame
        decoded_objects = decode(frame_rgb)
        if decoded_objects:
            for obj in decoded_objects:
                qr_code_data = obj.data.decode('utf-8')

                # Check if the QR code has already been processed
                if qr_code_data not in st.session_state.processed_qr_codes:
                    if mark_attendance(qr_code_data):
                        st.success(f"Attendance marked for QR code: {qr_code_data}")
                        st.session_state.processed_qr_codes.add(qr_code_data)
                    else:
                        pass
                else:
                    pass

    except RuntimeError:
        st.error("Failed to grab frame")
        break

    # Stop when the checkbox is unchecked
    if not run:
        break
