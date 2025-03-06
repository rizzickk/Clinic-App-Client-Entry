import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read()

# Display Title and Description
st.title("Client Tracker")
st.markdown("This is a simple Client Management System that allows you to input data.")

# Updated Staff list
DOCTORS = [
    "Dr. Jon Pierson",
    "Dr. Javier De La Torre",
    "Dr. John Borrego",
    "Dr. Omer Usman",
    "Dr. Abhinav Vulisha",
    "Dr. Muhammad Tahir",
    "Dr. Richard McCallum",
    "Dr. Eric Cox",
    "Dr. Sandra Vexler",
    "Dr. Abdel Vexler"
]

# Room options
ROOMS = ["100", "101", "102", "103"]

# Updated Appointment Types
APPT_TYPES = [
    "New Patient", 
    "New Encounter (existing pt.)", 
    "Follow-up", 
    "Lab Draw", 
    "Lab Results", 
    "Rx Refill", 
    "Specialist", 
    "Specialist Follow Up", 
    "Other"
]

# Form for user input
with st.form("client_tracker_form"):
    date = st.date_input("Date")
    staff = st.selectbox("Staff", options=DOCTORS, index=None)
    room = st.selectbox("Room", options=ROOMS, index=None)
    id_ = st.number_input("ID", min_value=0, max_value=1000000)

    # Appointment Type selection with editable option for "Other"
    appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=None)
    if appointment_type == "Other":
        appointment_type = st.text_input("Specify Other Appointment Type")

    # Time fields
    registration_start = st.time_input("Registration Start")
    registration_end = st.time_input("Registration End")
    triage_start = st.time_input("Triage Start")
    triage_end = st.time_input("Triage End")
    time_roomed = st.time_input("Time Roomed")
    exam_end = st.time_input("Exam End")
    doctor_in = st.time_input("Doctor In")
    doctor_out = st.time_input("Doctor Out")
    lab_start = st.time_input("Lab Start")
    lab_end = st.time_input("Lab End")
    sw_start = st.time_input("SW Start")
    sw_end = st.time_input("SW End")
    time_out = st.time_input("Time Out")

    submit_button = st.form_submit_button(label="Add Client")

    if submit_button:
        new_entry = pd.DataFrame({
            "Date": [date.strftime("%m/%d/%Y")],
            "Staff": [staff],
            "Room": [room],
            "ID": [id_],
            "Appointment Type": [appointment_type],
            "Registration Start": [registration_start.strftime('%H:%M')],
            "Registration End": [registration_end.strftime("%H:%M")],
            "Triage Start": [triage_start.strftime('%H:%M')],
            "Triage End": [triage_end.strftime('%H:%M')],
            "Time Roomed": [time_roomed.strftime('%H:%M')],
            "Exam End": [exam_end.strftime('%H:%M')],
            "Doctor In": [doctor_in.strftime('%H:%M')],
            "Doctor Out": [doctor_out.strftime('%H:%M')],
            "Lab Start": [lab_start.strftime('%H:%M')],
            "Lab End": [lab_end.strftime('%H:%M')],
            "SW Start": [sw_start.strftime('%H:%M')],
            "SW End": [sw_end.strftime('%H:%M')],
            "Time Out": [time_out.strftime('%H:%M')]
        })

        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(data=updated_data)

        st.success("Client added successfully!")