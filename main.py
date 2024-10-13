import streamlit as st
import qrcode
import sqlite3
import io
from PIL import Image
import cv2
import numpy as np
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

        # Create the attendance table if it does not exist
        c.execute(f'''CREATE TABLE IF NOT EXISTS attendance_log (
                        student_id INTEGER,
                        attendance_date DATE,
                        attended INTEGER,
                        PRIMARY KEY (student_id, attendance_date),
                        FOREIGN KEY(student_id) REFERENCES students(id)
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
st.write("Upload a QR Code image to mark attendance")

# Allow the user to upload an image
uploaded_file = st.file_uploader("Choose a QR code image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded QR Code', use_column_width=True)

    # Convert the image to an array and detect QR code
    img_array = np.array(image)
    qr_detector = cv2.QRCodeDetector()
    qr_code_data, _, _ = qr_detector(img_array)

    if qr_code_data:
        st.write(f"QR Code detected: {qr_code_data}")

        if mark_attendance(qr_code_data):
            st.success(f"Attendance marked for QR code: {qr_code_data}")
        else:
            st.error("QR Code not recognized")
    else:
        st.error("No QR Code found in the image.")
