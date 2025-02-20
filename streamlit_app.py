import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

#Display Title and Description
st.title("Client Tracker")
st.markdown("This is a simple Client Management System that allows you to input data.")

#Establish connection to Google Sheets
conn = st.connection("gsheets", type = GSheetsConnection)

#Fetch existing data
existing_data = conn.read(worksheet = "Sheet1", usecols = list(range(8)), ttl = 5)
existing_data = existing_data.dropna(how = "all")

#List of doctors, patient types, and appointment types
DOCTORS = [
    "Dr. Jon Pierson",
    "Dr. Javier De La Torre",
    "Dr. Chinyere Mbagwu",
    "Dr. Richard McCallum"
]

ROOM = [
    "100",
    "101",
    "102",
    "103"
]

APPOINTMENT_TYPE = [
    "COVID",
    "General",
    "LAB"
]

PATIENT_TYPE = [
    "NEW",
    "FP"
]

with st.form(key = "add_client"):
    #Input fields
    date = st.date_input("Date")
    staff = st.selectbox("Staff", options = DOCTORS, index = None)
    room = st.selectbox("Room", options = ROOM, index = None)
    id_ = st.number_input("ID", min_value = 0, max_value = 1000000)
    patient_type = st.selectbox("Patient Type", options = PATIENT_TYPE, index = None)   
    appointment_type = st.selectbox("Appointment Type", options = APPOINTMENT_TYPE, index = None)   
    registration_begin = st.time_input("Registration Begin Time")
    registration_end = st.time_input("Time Out")

    submit_button = st.form_submit_button(label = "Add Client")

    if submit_button:
        add_client = pd.DataFrame({
            "Date": [date],
            "Staff": [staff],
            "Room": [room],
            "ID": [id_],
            "Patient Type": [patient_type],
            "Appointment Type": [appointment_type],
            "Registration Begin Time": [registration_begin],
            "Time Out": [registration_end]
        })

        existing_data = pd.concat([existing_data, add_client], ignore_index = True)
        conn.update(worksheet = "Sheet1", data = existing_data)

        st.success("Client added successfully!")