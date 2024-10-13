import streamlit as st
import qrcode
import sqlite3
import io
import random
import string
from PIL import Image

# Function to generate a random QR code string
def generate_qr_code_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Function to generate QR code image
def generate_qr_code(qr_string):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Function to save student details in the SQLite database
def save_student_details(student_name, qr_string, student_year, student_class):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, qr_code TEXT, year TEXT, class TEXT)''')
    c.execute("INSERT INTO students (name, qr_code, year, class) VALUES (?, ?, ?, ?)", (student_name, qr_string, student_year, student_class))
    conn.commit()
    conn.close()

# Streamlit app interface
st.title("Student Attendance QR Code Generator")

student_name = st.text_input("Enter Student Name:")
student_year = st.text_input("Enter Student Year:")
student_class = st.text_input("Enter Student class:")

if st.button("Generate QR Code"):
    if student_name:
        qr_code_string = generate_qr_code_string()
        st.session_state[student_name] = [qr_code_string, student_year,student_class]
        qr_image = generate_qr_code(qr_code_string)

        # Show the QR code image
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format="PNG")
        st.image(img_buffer, caption="Generated QR Code", use_column_width=True)

    else:
        st.error("Please enter the student's name.")

apply_button = st.button("Apply")
if apply_button:
    if student_name:
        st.write(student_name)
        save_student_details(student_name, st.session_state[student_name][0],st.session_state[student_name][1],st.session_state[student_name][2])
        st.success(f"QR Code and details saved for {student_name}!")
    else:
        st.error("Please enter the student's name.")