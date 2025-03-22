import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Use America/Denver for Mountain Time with DST support
today_local = datetime.now(ZoneInfo("America/Denver")).date()


# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(ttl=0)

# ----------------- Helper Functions -----------------
def safe_to_datetime(value, fmt=None):
    """
    Safely converts a value to a datetime object.
    Returns None if the value is missing, empty, or invalid.
    """
    if pd.isna(value) or value in ["", None]:
        return None
    try:
        if fmt:
            return pd.to_datetime(value, format=fmt, errors="coerce")
        else:
            return pd.to_datetime(value, errors="coerce")
    except Exception:
        return None

def safe_to_time(value, fmt="%H:%M"):
    """
    Converts a value (assumed to be a string in a given format) to a time object.
    Returns time(0, 0) as a default if conversion fails.
    """
    dt = safe_to_datetime(value, fmt=fmt)
    if dt is not None:
        return dt.time()
    return time(0, 0)

# ----------------- App UI -----------------
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





# ----------------- NEW PATIENT FORM -----------------
if option == "New Patient":
    st.subheader("New Patient Entry")

    # Toggle to view existing data
    if not existing_data.empty:
        show_table = st.checkbox("Show Existing Patient Data (Last 20 Entries)", value=False)
        if show_table:
            # Convert "Date" to a datetime object.
            existing_data["Date_dt"] = pd.to_datetime(existing_data["Date"], format="%m/%d/%Y", errors="coerce")
            
            # Convert "Registration Start" into a timedelta (assuming it's in HH:MM format)
            # We append ":00" to represent seconds.
            existing_data["Registration_Start_td"] = pd.to_timedelta(existing_data["Registration Start"] + ":00")
            
            # Sort by ascending date and descending registration start time.
            sorted_data = existing_data.sort_values(by=["Date_dt", "Registration_Start_td"], ascending=[True, False])
            
            # Optionally drop the helper columns.
            sorted_data = sorted_data.drop(columns=["Date_dt", "Registration_Start_td"])
            
            # Display the top 20 entries.
            st.dataframe(sorted_data.head(20))
    else:
        st.warning("No data available yet.")

    # Append "Other" to your doctor list
    doctor_options = DOCTORS + ["Other"]
    staff = st.selectbox("Staff", options=doctor_options)
    
    # If "Other" is selected, prompt for a custom doctor name.
    if staff == "Other":
        other_staff = st.text_input("Enter Doctor Name", placeholder="Enter doctor's name")
    else:
        other_staff = ""
    
    # Use the custom name if "Other" was chosen; otherwise use the selected name.
    final_staff = staff if staff != "Other" else other_staff

    with st.form("new_patient_form"):

        date = st.date_input("Date", today_local)
        st.write("Selected Doctor:", final_staff)
        room = st.selectbox("Room", options=ROOMS, index=None)
        id_ = st.number_input("ID", min_value=0, max_value=1000000)

        # Select an appointment type
        appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=None, placeholder="Select an option")
        appointment_type_other = st.text_input("Describe Appointment Type if Applicable")

        # Time fields
        registration_start = st.time_input("Registration Start", value=time(0,0), step=60)
        registration_end = st.time_input("Registration End", value=time(0,0), step=60)
        triage_start = st.time_input("Triage Start", value=time(0,0), step=60)
        triage_end = st.time_input("Triage End", value=time(0,0), step=60)
        time_roomed = st.time_input("Time Roomed", value=time(0,0), step=60)
        exam_end = st.time_input("Exam End", value=time(0,0), step=60)
        doctor_in = st.time_input("Doctor In", value=time(0,0),step=60)
        doctor_out = st.time_input("Doctor Out", value=time(0,0), step=60)
        lab_start = st.time_input("Lab Start", value=time(0,0), step=60)
        lab_end = st.time_input("Lab End", value=time(0,0), step=60)
        sw_start = st.time_input("SW Start", value=time(0,0), step=60)
        sw_end = st.time_input("SW End", value=time(0,0), step=60)
        time_out = st.time_input("Time Out", value=time(0,0), step=60)

        submit_button = st.form_submit_button(label="Add Patient")

        if submit_button:
            new_entry = pd.DataFrame({
                "Date": [date.strftime("%m/%d/%Y")],
                "Staff": [final_staff],
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




# ----------------- EDIT EXISTING PATIENT FORM -----------------

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
        # Retrieve the stored doctor value from Google Sheets
        stored_doctor = str(patient_data.get("Staff", "")).strip()
        
        # Determine default selection: if the stored doctor is in DOCTORS, use that;
        # otherwise, default to "Other" and prefill the text input with the stored doctor name.
        if stored_doctor in DOCTORS:
            default_selection = stored_doctor
            default_other = ""
        else:
            default_selection = "Other"
            default_other = stored_doctor
        
        # Create the doctor options list
        doctor_options = DOCTORS + ["Other"]
        
        # Place the selectbox outside the form for reactivity
        staff_selection = st.selectbox("Staff", options=doctor_options, index=doctor_options.index(default_selection))
        
        # Show text input if "Other" is selected, prefilled with stored value if available
        if staff_selection == "Other":
            other_staff = st.text_input("Enter Doctor Name", value=default_other, placeholder="Enter doctor's name")
        else:
            other_staff = ""
        
        # Determine final doctor value
        final_staff = staff_selection if staff_selection != "Other" else other_staff
    
    if selected_id and patient_data:
            # Safely prepopulate fields using helper functions
            stored_date = safe_to_datetime(patient_data.get("Date"), fmt="%m/%d/%Y")
            default_date = stored_date.date() if stored_date is not None else today_local

            # Prepopulate doctor info
            stored_staff = str(patient_data.get("Staff", "")).strip()
            if stored_staff in DOCTORS:
                default_staff = stored_staff
                default_other = ""
            else:
                default_staff = "Other"
                default_other = stored_staff
            doctor_options = DOCTORS + ["Other"]
            # Doctor selection outside the form for immediate reactivity
            staff_selection = st.selectbox("Staff", options=doctor_options, index=doctor_options.index(default_staff))
            if staff_selection == "Other":
                other_staff = st.text_input("Enter Doctor Name", value=default_other, placeholder="Enter doctor's name")
            else:
                other_staff = ""
            final_staff = staff_selection if staff_selection != "Other" else other_staff

            # Prepopulate room field safely
            stored_room = str(patient_data.get("Room", "")).strip()
            try:
                room_value = str(int(float(stored_room))) if stored_room not in ["", "nan", "NaN"] else ROOMS[0]
            except Exception:
                room_value = ROOMS[0]
            room_index = ROOMS.index(room_value) if room_value in ROOMS else 0
            room = st.selectbox("Room", options=ROOMS, index=room_index)
            
            stored_appt = str(patient_data.get("Appointment Type", "")).strip() if patient_data.get("Appointment Type") else APPT_TYPES[0]
            appt_index = APPT_TYPES.index(stored_appt) if stored_appt in APPT_TYPES else 0
            appointment_type = st.selectbox("Appointment Type", options=APPT_TYPES, index=appt_index)
            
            existing_appt_desc = patient_data.get("Describe Appointment Type If Applicable", "")
            if pd.isna(existing_appt_desc):
                existing_appt_desc = ""
            appointment_type_other = st.text_input("Describe Appointment Type if Applicable", value=existing_appt_desc)
            
            # Safely prepopulate time fields
            stored_reg_start = safe_to_datetime(patient_data.get("Registration Start"), fmt="%H:%M")
            default_reg_start = stored_reg_start.time() if stored_reg_start is not None else time(0, 0)
            registration_start = st.time_input("Registration Start", value=default_reg_start, step=60)
            
            stored_reg_end = safe_to_datetime(patient_data.get("Registration End"), fmt="%H:%M")
            default_reg_end = stored_reg_end.time() if stored_reg_end is not None else time(0, 0)
            registration_end = st.time_input("Registration End", value=default_reg_end, step=60)
            
            stored_triage_start = safe_to_datetime(patient_data.get("Triage Start"), fmt="%H:%M")
            default_triage_start = stored_triage_start.time() if stored_triage_start is not None else time(0, 0)
            triage_start = st.time_input("Triage Start", value=default_triage_start, step=60)
            
            stored_triage_end = safe_to_datetime(patient_data.get("Triage End"), fmt="%H:%M")
            default_triage_end = stored_triage_end.time() if stored_triage_end is not None else time(0, 0)
            triage_end = st.time_input("Triage End", value=default_triage_end, step=60)
            
            stored_time_roomed = safe_to_datetime(patient_data.get("Time Roomed"), fmt="%H:%M")
            default_time_roomed = stored_time_roomed.time() if stored_time_roomed is not None else time(0, 0)
            time_roomed = st.time_input("Time Roomed", value=default_time_roomed, step=60)
            
            stored_exam_end = safe_to_datetime(patient_data.get("Exam End"), fmt="%H:%M")
            default_exam_end = stored_exam_end.time() if stored_exam_end is not None else time(0, 0)
            exam_end = st.time_input("Exam End", value=default_exam_end, step=60)
            
            stored_doc_in = safe_to_datetime(patient_data.get("Doctor In"), fmt="%H:%M")
            default_doc_in = stored_doc_in.time() if stored_doc_in is not None else time(0, 0)
            doctor_in = st.time_input("Doctor In", value=default_doc_in, step=60)
            
            stored_doc_out = safe_to_datetime(patient_data.get("Doctor Out"), fmt="%H:%M")
            default_doc_out = stored_doc_out.time() if stored_doc_out is not None else time(0, 0)
            doctor_out = st.time_input("Doctor Out", value=default_doc_out, step=60)
            
            stored_lab_start = safe_to_datetime(patient_data.get("Lab Start"), fmt="%H:%M")
            default_lab_start = stored_lab_start.time() if stored_lab_start is not None else time(0, 0)
            lab_start = st.time_input("Lab Start", value=default_lab_start, step=60)
            
            stored_lab_end = safe_to_datetime(patient_data.get("Lab End"), fmt="%H:%M")
            default_lab_end = stored_lab_end.time() if stored_lab_end is not None else time(0, 0)
            lab_end = st.time_input("Lab End", value=default_lab_end, step=60)
            
            stored_sw_start = safe_to_datetime(patient_data.get("SW Start"), fmt="%H:%M")
            default_sw_start = stored_sw_start.time() if stored_sw_start is not None else time(0, 0)
            sw_start = st.time_input("SW Start", value=default_sw_start, step=60)
            
            stored_sw_end = safe_to_datetime(patient_data.get("SW End"), fmt="%H:%M")
            default_sw_end = stored_sw_end.time() if stored_sw_end is not None else time(0, 0)
            sw_end = st.time_input("SW End", value=default_sw_end, step=60)
            
            stored_time_out = safe_to_datetime(patient_data.get("Time Out"), fmt="%H:%M")
            default_time_out = stored_time_out.time() if stored_time_out is not None else time(0, 0)
            time_out = st.time_input("Time Out", value=default_time_out, step=60)
            
            with st.form("edit_patient_form"):
                date = st.date_input("Date", value=default_date)
                st.write("Selected Doctor:", final_staff)
                # Add additional fields as needed here...
                
                update_button = st.form_submit_button(label="Update Patient")
                if update_button:
                    # Identify the existing entry by matching ID and Date
                    existing_entry = existing_data[
                        (existing_data["ID"] == selected_id) &
                        (existing_data["Date"] == date.strftime("%m/%d/%Y"))
                    ]
                    if not existing_entry.empty:
                        existing_data.loc[
                            (existing_data["ID"] == selected_id) &
                            (existing_data["Date"] == date.strftime("%m/%d/%Y")),
                            ["Staff", "Room", "Appointment Type", "Describe Appointment Type If Applicable",
                            "Registration Start", "Registration End", "Triage Start", "Triage End", "Time Roomed",
                            "Exam End", "Doctor In", "Doctor Out", "Lab Start", "Lab End", "SW Start", "SW End", "Time Out"]
                        ] = [
                            final_staff, room, appointment_type, appointment_type_other,
                            registration_start.strftime('%H:%M') if registration_start else None,
                            registration_end.strftime('%H:%M') if registration_end else None,
                            triage_start.strftime('%H:%M') if triage_start else None,
                            triage_end.strftime('%H:%M') if triage_end else None,
                            time_roomed.strftime('%H:%M') if time_roomed else None,
                            exam_end.strftime('%H:%M') if exam_end else None,
                            doctor_in.strftime('%H:%M') if doctor_in else None,
                            doctor_out.strftime('%H:%M') if doctor_out else None,
                            lab_start.strftime('%H:%M') if lab_start else None,
                            lab_end.strftime('%H:%M') if lab_end else None,
                            sw_start.strftime('%H:%M') if sw_start else None,
                            sw_end.strftime('%H:%M') if sw_end else None,
                            time_out.strftime('%H:%M') if time_out else None
                        ]
                        conn.update(data=existing_data)
                        st.success("Patient information updated successfully!")
                    else:
                        new_entry = pd.DataFrame({
                            "Date": [date.strftime("%m/%d/%Y")],
                            "ID": [selected_id],
                            "Staff": [final_staff],
                            "Room": [room],
                            "Appointment Type": [appointment_type],
                            "Describe Appointment Type If Applicable": [appointment_type_other],
                            "Registration Start": [registration_start.strftime('%H:%M') if registration_start else None],
                            "Registration End": [registration_end.strftime('%H:%M') if registration_end else None],
                            "Triage Start": [triage_start.strftime('%H:%M') if triage_start else None],
                            "Triage End": [triage_end.strftime('%H:%M') if triage_end else None],
                            "Time Roomed": [time_roomed.strftime('%H:%M') if time_roomed else None],
                            "Exam End": [exam_end.strftime('%H:%M') if exam_end else None],
                            "Doctor In": [doctor_in.strftime('%H:%M') if doctor_in else None],
                            "Doctor Out": [doctor_out.strftime('%H:%M') if doctor_out else None],
                            "Lab Start": [lab_start.strftime('%H:%M') if lab_start else None],
                            "Lab End": [lab_end.strftime('%H:%M') if lab_end else None],
                            "SW Start": [sw_start.strftime('%H:%M') if sw_start else None],
                            "SW End": [sw_end.strftime('%H:%M') if sw_end else None],
                            "Time Out": [time_out.strftime('%H:%M') if time_out else None]
                        })
                        if existing_data.empty:
                            updated_data = new_entry
                        else:
                            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
                        conn.update(data=updated_data)
                        st.success("Patient information updated successfully!")



st.subheader("Clinic Metrics")

if not existing_data.empty:
    total_patients = len(existing_data)
    today_str = today_local.strftime("%m/%d/%Y")
    patients_today = len(existing_data[existing_data["Date"] == today_str])
    common_appt = existing_data["Appointment Type"].mode()[0] if not existing_data["Appointment Type"].isna().all() else "N/A"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Total Patients</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{total_patients}</p>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<p style="font-size:16px; font-weight:bold;">Patients Seen Today</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;">{patients_today}</p>', unsafe_allow_html=True)

    with col3:
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