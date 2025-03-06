import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read()

# Display Title and Description
st.title("Client Tracker")
st.markdown("This is a simple Client Management System that allows you to input and update patient records.")

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

# Function to get existing patient data by ID
def get_patient_data(patient_id):
    """Retrieve existing patient data based on ID."""
    if patient_id in existing_data["ID"].values:
        return existing_data.loc[existing_data["ID"] == patient_id].to_dict(orient="records")[0]
    return None

# Allow user to select an existing patient for editing
st.subheader("Edit Existing Patient")
selected_id = st.number_input("Enter Patient ID to Edit", min_value=0, max_value=1000000, step=1)

if selected_id:
    patient_data = get_patient_data(selected_id)
    if patient_data:
        st.success("Patient found! Modify the details below and click 'Update'.")
    else:
        st.warning("No matching patient ID found.")

# If a valid patient is selected, prefill the form
if selected_id and patient_data:
    with st.form("edit_client_form"):
        date = st.date_input("Date", value=pd.to_datetime(patient_data["Date"]))
        staff = st.selectbox("Staff", options=DOCTORS, index=DOCTORS.index(patient_data["Staff"]))
        room = st.selectbox("Room", options=ROOMS, index=ROOMS.index(str(patient_data["Room"])))
        appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=APPT_TYPES.index(patient_data["Appointment Type"]) if patient_data["Appointment Type"] in APPT_TYPES else len(APPT_TYPES)-1)
        
        if appointment_type == "Other":
            appointment_type = st.text_input("Specify Other Appointment Type", value=patient_data["Appointment Type"])

        # Time fields pre-filled
        registration_start = st.time_input("Registration Start", value=pd.to_datetime(patient_data["Registration Start"]).time())
        registration_end = st.time_input("Registration End", value=pd.to_datetime(patient_data["Registration End"]).time())
        triage_start = st.time_input("Triage Start", value=pd.to_datetime(patient_data["Triage Start"]).time())
        triage_end = st.time_input("Triage End", value=pd.to_datetime(patient_data["Triage End"]).time())
        time_roomed = st.time_input("Time Roomed", value=pd.to_datetime(patient_data["Time Roomed"]).time())
        exam_end = st.time_input("Exam End", value=pd.to_datetime(patient_data["Exam End"]).time())
        doctor_in = st.time_input("Doctor In", value=pd.to_datetime(patient_data["Doctor In"]).time())
        doctor_out = st.time_input("Doctor Out", value=pd.to_datetime(patient_data["Doctor Out"]).time())
        lab_start = st.time_input("Lab Start", value=pd.to_datetime(patient_data["Lab Start"]).time())
        lab_end = st.time_input("Lab End", value=pd.to_datetime(patient_data["Lab End"]).time())
        sw_start = st.time_input("SW Start", value=pd.to_datetime(patient_data["SW Start"]).time())
        sw_end = st.time_input("SW End", value=pd.to_datetime(patient_data["SW End"]).time())
        time_out = st.time_input("Time Out", value=pd.to_datetime(patient_data["Time Out"]).time())

        update_button = st.form_submit_button(label="Update Patient")

        if update_button:
            # Update DataFrame
            existing_data.loc[existing_data["ID"] == selected_id, :] = [
                date.strftime("%m/%d/%Y"), staff, room, selected_id, appointment_type,
                registration_start.strftime('%H:%M'), registration_end.strftime('%H:%M'),
                triage_start.strftime('%H:%M'), triage_end.strftime('%H:%M'),
                time_roomed.strftime('%H:%M'), exam_end.strftime('%H:%M'),
                doctor_in.strftime('%H:%M'), doctor_out.strftime('%H:%M'),
                lab_start.strftime('%H:%M'), lab_end.strftime('%H:%M'),
                sw_start.strftime('%H:%M'), sw_end.strftime('%H:%M'),
                time_out.strftime('%H:%M')
            ]

            # Save updated data
            conn.update(data=existing_data)
            st.success("Patient information updated successfully!")