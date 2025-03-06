import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read()

# Display Title
st.title("Client Tracker")

# Selection for New Patient or Edit Patient
option = st.radio("Select an option:", ["New Patient", "Edit Patient"])

# Updated Staff list
DOCTORS = [
    "Dr. Jon Pierson", "Dr. Javier De La Torre", "Dr. John Borrego", "Dr. Omer Usman",
    "Dr. Abhinav Vulisha", "Dr. Muhammad Tahir", "Dr. Richard McCallum",
    "Dr. Eric Cox", "Dr. Sandra Vexler", "Dr. Abdel Vexler"
]

# Room options
ROOMS = ["100", "101", "102", "103"]

# Updated Appointment Types
APPT_TYPES = [
    "New Patient", "New Encounter (existing pt.)", "Follow-up",
    "Lab Draw", "Lab Results", "Rx Refill", "Specialist", "Specialist Follow Up", "Other"
]

# Function to get existing patient data by ID
def get_patient_data(patient_id):
    """Retrieve existing patient data based on ID."""
    if patient_id in existing_data["ID"].values:
        return existing_data.loc[existing_data["ID"] == patient_id].to_dict(orient="records")[0]
    return None

# ---- NEW PATIENT FORM ----
if option == "New Patient":
    st.subheader("New Patient Entry")
    with st.form("new_patient_form"):
        date = st.date_input("Date")
        staff = st.selectbox("Staff", options=DOCTORS, index=None)
        room = st.selectbox("Room", options=ROOMS, index=None)
        id_ = st.number_input("ID", min_value=0, max_value=1000000)

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

        submit_button = st.form_submit_button(label="Add Patient")

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

            if existing_data.empty:
                updated_data = new_entry
            else:
                updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
            
            conn.update(data=updated_data)

            st.success("Patient added successfully!")

# ---- EDIT EXISTING PATIENT FORM ----
elif option == "Edit Patient":
    st.subheader("Edit Existing Patient")

    selected_id = st.number_input("Enter Patient ID to Edit", min_value=0, max_value=1000000, step=1)
    
    if selected_id:
        patient_data = get_patient_data(selected_id)
        if patient_data:
            st.success("Patient found! Modify the details below and click 'Update'.")
        else:
            st.warning("No matching patient ID found.")

    if selected_id and patient_data:
        with st.form("edit_patient_form"):
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

            update_button = st.form_submit_button(label="Update Patient")

            if update_button:
                existing_data.loc[existing_data["ID"] == selected_id, :] = [
                    date.strftime("%m/%d/%Y"), staff, room, selected_id, appointment_type,
                    registration_start.strftime('%H:%M'), registration_end.strftime('%H:%M'),
                    triage_start.strftime('%H:%M'), triage_end.strftime('%H:%M'),
                    time_roomed.strftime('%H:%M'), exam_end.strftime('%H:%M')
                ]

                conn.update(data=existing_data)
                st.success("Patient information updated successfully!")