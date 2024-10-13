import streamlit as st
import qrcode
import sqlite3
import io
from PIL import Image
import cv2
import numpy as np
from datetime import date

# Function to get student name by QR code
def get_student_name(qr_code):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Get student name using the qr_code
    c.execute("SELECT name FROM students WHERE qr_code = ?", (qr_code,))
    result = c.fetchone()

    conn.close()
    return result[0] if result else None

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
        return student_id  # Return student ID for name lookup
    else:
        conn.close()
        return None


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
    qcd = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(img_array)

    if retval:
        st.write(f"QR Code detected: {decoded_info}")

        student_id = mark_attendance(decoded_info[0])
        if student_id:
            # Get the student's name
            student_name = get_student_name(decoded_info[0])
            if student_name:
                st.success(f"Attendance marked for {student_name}!")
            else:
                st.error("Student name not found.")
        else:
            st.error("QR Code not recognized.")
    else:
        st.error("No QR Code found in the image.")
