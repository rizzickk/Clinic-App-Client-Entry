import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd




# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(ttl=0)

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

from datetime import datetime, timezone, timedelta

# Define the UTC offset for Mountain Time (MST/MDT)
MOUNTAIN_TIME_OFFSET = timedelta(hours=-7)  # MST is UTC-7, MDT is UTC-6

# Get today's date in Mountain Time
today_local = datetime.now(timezone.utc) + MOUNTAIN_TIME_OFFSET
today_local = today_local.date()  # Extract only the date

# ---- NEW PATIENT FORM ----
if option == "New Patient":
    st.subheader("New Patient Entry")

    # Toggle to view existing data
    if not existing_data.empty:
        show_table = st.checkbox("Show Existing Patient Data (Last 20 Entries)", value=False)
        if show_table:
            st.dataframe(existing_data.tail(20))
    else:
        st.warning("No data available yet.")

    with st.form("new_patient_form"):
        date = st.date_input("Date", today_local)
        staff = st.selectbox("Staff", options=DOCTORS, index=None)
        room = st.selectbox("Room", options=ROOMS, index=None)
        id_ = st.number_input("ID", min_value=0, max_value=1000000)

        # Select an appointment type
        appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=None, placeholder="Select an option")
        appointment_type_other = st.text_input("Describe Appointment Type if Applicable")
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
                "Describe Appointment Type If Applicable": [appointment_type_other],
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
    
    # Toggle to view existing data
    if not existing_data.empty:
        show_table = st.checkbox("Show Existing Patient Data (Last 20 Entries)", value=False)
        if show_table:
            st.dataframe(existing_data)
    else:
        st.warning("No data available yet.")

    if selected_id:
        patient_data = get_patient_data(selected_id)
        if patient_data:
            st.success("Patient found! Modify the details below and click 'Update'.")
        else:
            st.warning("No matching patient ID found.")

    if selected_id and patient_data:
        with st.form("edit_patient_form"):
            date = st.date_input("Date", value=pd.to_datetime(patient_data["Date"]))
            staff_value = str(patient_data.get("Staff", "")).strip() if patient_data.get("Staff") else DOCTORS[0]
            staff_index = DOCTORS.index(staff_value) if staff_value in DOCTORS else 0  # Default to index 0 if not found
            staff = st.selectbox("Staff", options=DOCTORS, index=staff_index)
            room_value = str(int(patient_data.get("Room", 0))) if patient_data.get("Room") not in [None, ""] else ROOMS[0]
            room_index = ROOMS.index(room_value) if room_value in ROOMS else 0
            room = st.selectbox("Room", options=ROOMS, index=room_index)
            appt_value = str(patient_data["Appointment Type"]).strip() if "Appointment Type" in patient_data and patient_data["Appointment Type"] is not None else APPT_TYPES[0]
            appt_index = APPT_TYPES.index(appt_value) if appt_value in APPT_TYPES else 0  # Default to first option if not found
            appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=appt_index)
            appointment_type_other = st.text_input("Describe Appointment Type if Applicable")

            # Time fields pre-filled
            registration_start = st.time_input("Registration Start", value=pd.to_datetime(patient_data["Registration Start"]).time() if patient_data["Registration Start"] else None)
            registration_end = st.time_input("Registration End", value=pd.to_datetime(patient_data["Registration End"]).time() if patient_data["Registration End"] else None)
            triage_start = st.time_input("Triage Start", value=pd.to_datetime(patient_data["Triage Start"]).time() if patient_data["Triage Start"] else None)
            triage_end = st.time_input("Triage End", value=pd.to_datetime(patient_data["Triage End"]).time() if patient_data["Triage End"] else None)
            time_roomed = st.time_input("Time Roomed", value=pd.to_datetime(patient_data["Time Roomed"]).time() if patient_data["Time Roomed"] else None)
            exam_end = st.time_input("Exam End", value=pd.to_datetime(patient_data["Exam End"]).time() if patient_data["Exam End"] else None)
            doctor_in = st.time_input("Doctor In", value=pd.to_datetime(patient_data["Doctor In"]).time() if patient_data["Doctor In"] else None)
            doctor_out = st.time_input("Doctor Out", value=pd.to_datetime(patient_data["Doctor Out"]).time() if patient_data["Doctor Out"] else None)
            lab_start = st.time_input("Lab Start", value=pd.to_datetime(patient_data["Lab Start"]).time() if patient_data["Lab Start"] else None)
            lab_end = st.time_input("Lab End", value=pd.to_datetime(patient_data["Lab End"]).time() if patient_data["Lab End"] else None)
            sw_start = st.time_input("SW Start", value=pd.to_datetime(patient_data["SW Start"]).time() if patient_data["SW Start"] else None)
            sw_end = st.time_input("SW End", value=pd.to_datetime(patient_data["SW End"]).time() if patient_data["SW End"] else None)
            time_out = st.time_input("Time Out", value=pd.to_datetime(patient_data["Time Out"]).time() if patient_data["Time Out"] else None)
                        
            update_button = st.form_submit_button(label="Update Patient")

            if update_button:
                # Ensure selected_id exists in the DataFrame before modifying
                if not existing_data[existing_data["ID"] == selected_id].empty:
                    existing_data.loc[existing_data["ID"] == selected_id, "Date"] = date.strftime("%m/%d/%Y")
                    existing_data.loc[existing_data["ID"] == selected_id, "Staff"] = staff
                    existing_data.loc[existing_data["ID"] == selected_id, "Room"] = room
                    existing_data.loc[existing_data["ID"] == selected_id, "Appointment Type"] = appointment_type
                    existing_data.at[existing_data.index[existing_data["ID"] == selected_id][0], "Describe Appointment Type If Applicable"] = appointment_type_other
                    existing_data.loc[existing_data["ID"] == selected_id, "Registration Start"] = registration_start.strftime('%H:%M') if registration_start else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Registration End"] = registration_end.strftime('%H:%M') if registration_end else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Triage Start"] = triage_start.strftime('%H:%M') if triage_start else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Triage End"] = triage_end.strftime('%H:%M') if triage_end else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Time Roomed"] = time_roomed.strftime('%H:%M') if time_roomed else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Exam End"] = exam_end.strftime('%H:%M') if exam_end else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Doctor In"] = doctor_in.strftime('%H:%M') if doctor_in else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Doctor Out"] = doctor_out.strftime('%H:%M') if doctor_out else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Lab Start"] = lab_start.strftime('%H:%M') if lab_start else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Lab End"] = lab_end.strftime('%H:%M') if lab_end else None
                    existing_data.loc[existing_data["ID"] == selected_id, "SW Start"] = sw_start.strftime('%H:%M') if sw_start else None
                    existing_data.loc[existing_data["ID"] == selected_id, "SW End"] = sw_end.strftime('%H:%M') if sw_end else None
                    existing_data.loc[existing_data["ID"] == selected_id, "Time Out"] = time_out.strftime('%H:%M') if time_out else None

                    # Update the Google Sheets data
                    conn.update(data=existing_data)
                    st.success("Patient information updated successfully!")
                else:
                    st.error("Error: Patient ID not found. Please try again.")

st.subheader("Clinic Metrics")

if not existing_data.empty:
    # Total Patients Recorded
    total_patients = len(existing_data)

    # Patients Seen Today
    today_str = today_local.strftime("%m/%d/%Y")  # Format it as MM/DD/YYYY
    patients_today = len(existing_data[existing_data["Date"] == today_str])

    # Average Time Spent in Clinic (Time Out - Registration Start)
    existing_data["Registration Start"] = pd.to_datetime(existing_data["Registration Start"], errors="coerce")
    existing_data["Time Out"] = pd.to_datetime(existing_data["Time Out"], errors="coerce")
    existing_data["Total Time"] = (existing_data["Time Out"] - existing_data["Registration Start"]).dt.total_seconds() / 60  # Convert to minutes
    avg_time_spent = existing_data["Total Time"].mean()

    # Average Doctor Consultation Time (Doctor Out - Doctor In)
    existing_data["Doctor In"] = pd.to_datetime(existing_data["Doctor In"], errors="coerce")
    existing_data["Doctor Out"] = pd.to_datetime(existing_data["Doctor Out"], errors="coerce")
    existing_data["Doctor Time"] = (existing_data["Doctor Out"] - existing_data["Doctor In"]).dt.total_seconds() / 60  # Convert to minutes
    avg_doctor_time = existing_data["Doctor Time"].mean()

    # Most Common Appointment Type
    common_appt = existing_data["Appointment Type"].mode()[0] if not existing_data["Appointment Type"].isna().all() else "N/A"

    # Display Metrics with Smaller Font
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Total Patients</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{total_patients}</p>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Patients Seen Today</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{patients_today}</p>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Avg Time in Clinic (mins)</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{"{:.1f}".format(avg_time_spent) if pd.notna(avg_time_spent) else "N/A"}</p>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Avg Doctor Time (mins)</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{"{:.1f}".format(avg_doctor_time) if pd.notna(avg_doctor_time) else "N/A"}</p>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Most Common Appointment</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{common_appt}</p>', unsafe_allow_html=True)

else:
    st.warning("No data available for metrics.")

import matplotlib.pyplot as plt

st.divider()
st.subheader("📊 Clinic Data Insights")

today_str = today_local.strftime("%m/%d/%Y")  # Format it as MM/DD/YYYY

# Filter data for today's appointments
patients_today_df = existing_data[existing_data["Date"] == today_str]

# Count the number of patients seen per doctor
patients_per_doctor = patients_today_df["Staff"].value_counts()

st.subheader("Patients Seen per Doctor Today")

if not patients_today_df.empty and not patients_per_doctor.empty:
    # Option 1: Simple Bar Chart using Streamlit
    st.bar_chart(patients_per_doctor)

  
else:
    st.warning("No patients seen today.")