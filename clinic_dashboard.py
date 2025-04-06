#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 10:31:09 2025

@author: rizic
"""

import streamlit as st
import pandas as pd
import numpy as np

# Load data
@st.cache_data

def load_data():
    df = pd.read_csv("Cleaned_Clinic_Data_with_Valid_Durations.csv", parse_dates=[
        'Registration Start', 'Time Out', 'Doctor In', 'Doctor Out',
        'Triage Start', 'Triage End', 'Lab Start', 'Lab End',
        'SW Start', 'SW End', 'Time Roomed'])

    df['Total Visit Duration'] = (df['Time Out'] - df['Registration Start']).dt.total_seconds() / 60
    df['Doctor Time'] = (df['Doctor Out'] - df['Doctor In']).dt.total_seconds() / 60
    df['Triage Duration'] = (df['Triage End'] - df['Triage Start']).dt.total_seconds() / 60
    df['Lab Duration'] = (df['Lab End'] - df['Lab Start']).dt.total_seconds() / 60
    df['SW Duration'] = (df['SW End'] - df['SW Start']).dt.total_seconds() / 60
    df['Arrival to Room'] = (df['Time Roomed'] - df['Registration Start']).dt.total_seconds() / 60
    return df

df = load_data()

st.title("Clinic Operational Metrics Dashboard")

# Ensure 'Date' is datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Calculate min and max date
min_date = df['Date'].min().strftime('%B %d, %Y')
max_date = df['Date'].max().strftime('%B %d, %Y')

# Display as caption
st.caption(f"📅 Data covers visits from **{min_date}** to **{max_date}**.")

st.header("Overall Visit Metrics")
st.metric("Avg Total Visit Duration (min)", f"{df['Total Visit Duration'].mean():.1f}")
st.metric("Avg Doctor Time (min)", f"{df['Doctor Time'].mean():.1f}")


st.header("Doctor-level Metrics")

# Step 1: All patients with a staff assigned
doctor_assignments = df[df['Staff'].notna()]

# Step 2: Doctor time values for average calculation
doctor_time_data = df[df['Doctor Time'].notna() & df['Staff'].notna()]

# Step 3: Aggregate
avg_time = doctor_time_data.groupby('Staff')['Doctor Time'].mean()
patient_counts = doctor_assignments.groupby('Staff')['ID'].count()

# Step 4: Merge both into a single DataFrame
doc_stats = pd.DataFrame({
    'Avg Doctor Time (min)': avg_time.round(1),
    'Patient Count': patient_counts
}).fillna(0).sort_values(by='Patient Count', ascending=False)

st.dataframe(doc_stats)

st.header("Bottleneck Analysis")
bottlenecks = {
    'Triage': df['Triage Duration'].mean(),
    'Lab': df['Lab Duration'].mean(),
    'SW': df['SW Duration'].mean()
}
biggest = max(bottlenecks, key=bottlenecks.get)
st.write(f"**Biggest Bottleneck:** {biggest} ({bottlenecks[biggest]:.1f} min average)")

st.header("Flow Metrics")
total = len(df)
both_triage = df[['Triage Start', 'Triage End']].dropna().shape[0]
st.metric("Triage Path Coverage", f"{both_triage / total:.0%}")
# Add footnote explanation
st.caption("Percentage of patients that went through triage.")
st.metric("Avg Time from Arrival to Room (min)", f"{df['Arrival to Room'].mean():.1f}")

st.header("Visit Mix")
visit_mix = df['Visit Type'].value_counts(normalize=True) * 100
visit_mix = visit_mix.round(1)

st.bar_chart(visit_mix)
st.caption("FP - Follow-up Patient, NP - New Patient")

st.header("Visit Duration by Category (min)")

visit_duration_by_cat = (
    df.groupby('Visit Category')['Total Visit Duration']
    .mean()
    .round(1)
    .sort_values(ascending=False)
)

st.dataframe(visit_duration_by_cat)

import altair as alt

st.header("Visit Category Distribution")

# Clean and sort
cat_dist = (
    df['Visit Category']
    .loc[df['Visit Category'].str.lower() != 'other']
    .value_counts()
    .sort_values(ascending=False)
    .reset_index()
)

cat_dist.columns = ['Visit Category', 'Count']

# Altair bar chart with custom x-axis order
bar = alt.Chart(cat_dist).mark_bar().encode(
    x=alt.X('Visit Category', sort='-y'),  # Sort by count descending
    y='Count'
).properties(
    width=700,
    height=400
)

st.altair_chart(bar, use_container_width=True)


st.header("Top 5 Visit Categories")
st.write(cat_dist.head(5))

st.header("Weekly Visit Mix Change")

# Ensure 'Date' is datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Remove 'Other' visit categories (case-insensitive)
filtered_df = df[df['Visit Category'].str.lower() != 'other']

# Convert to weekly period start date
filtered_df['Week'] = filtered_df['Date'].dt.to_period('W').apply(lambda r: r.start_time)


# Ensure proper datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Filter out 'Other' (case insensitive)
filtered_df = df[df['Visit Category'].str.lower() != 'other']



# Ensure datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Exclude 'Other' categories
filtered_df = df[df['Visit Category'].str.lower() != 'other'].copy()

# Create a 'Month' column using first day of the month
filtered_df['Month'] = filtered_df['Date'].dt.to_period('M').apply(lambda r: r.start_time)

# Monthly visit mix (pivot table)
monthly_mix = (
    filtered_df.groupby(['Month', 'Visit Category'])
    .size()
    .unstack()
    .fillna(0)
)

if len(monthly_mix) >= 2:
    last_month = monthly_mix.iloc[-1]
    prev_month = monthly_mix.iloc[-2]

    # Only keep categories with activity in both months
    mask = (prev_month > 0) | (last_month > 0)
    last_month = last_month[mask]
    prev_month = prev_month[mask]

    # Compute % change with divide-by-zero handling
    delta = ((last_month - prev_month) / prev_month.replace(0, np.nan))

# Extract actual month names
    prev_label = prev_month.name.strftime("%B %Y")   # e.g., "February 2025"
    last_label = last_month.name.strftime("%B %Y")   # e.g., "March 2025"

# Build labeled DataFrame
    delta_df = pd.DataFrame({
    prev_label: prev_month.astype(int),
    last_label: last_month.astype(int),
    '% Change': delta.apply(lambda x: f"{x:+.1%}")
    }).sort_values(by='% Change', ascending=False).sort_values(by='% Change', ascending=False)

    st.dataframe(delta_df)
    st.caption("Month-over-month change in visit category mix.")
else:
    st.info("Not enough monthly data to compare trends.")
    st.caption("* Some values may be missing due to user entry issues. The clinic gets busy and cannot always track every input.")