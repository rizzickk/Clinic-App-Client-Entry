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

st.header("Overall Visit Metrics")
st.metric("Avg Total Visit Duration (min)", f"{df['Total Visit Duration'].mean():.1f}")
st.metric("Avg Doctor Time (min)", f"{df['Doctor Time'].mean():.1f}")

if 'Staff' in df.columns:
    st.header("Doctor-level Metrics")
    doc_df = df.dropna(subset=['Doctor Time', 'Staff'])
    doc_stats = doc_df.groupby('Staff').agg(
        Avg_Doctor_Time=('Doctor Time', 'mean'),
        Patients=('ID', 'count')
    )
    doc_stats['Avg_Doctor_Time'] = doc_stats['Avg_Doctor_Time'].round(1)

doc_stats = doc_stats.sort_values(by='Avg_Doctor_Time', ascending=False)
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

st.header("Visit Duration by Category")

visit_duration_by_cat = (
    df.groupby('Visit Category')['Total Visit Duration']
    .mean()
    .round(1)
    .sort_values(ascending=False)
)

st.dataframe(visit_duration_by_cat)

st.header("Visit Category Distribution")
cat_dist = df['Visit Category'].value_counts()
st.bar_chart(cat_dist)

st.header("Top 5 Visit Categories")
st.write(cat_dist.head(5))

st.header("Weekly Visit Mix Change")
# Correct way to set the weekly periods
# Explicit datetime conversion
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)

weekly_mix = df.groupby(['Week', 'Visit Category']).size().unstack().fillna(0)

if len(weekly_mix) >= 2:
    last_week = weekly_mix.iloc[-1]
    prev_week = weekly_mix.iloc[-2]
    delta = (last_week - prev_week) / prev_week.replace(0, np.nan)
    st.dataframe(delta.dropna().sort_values(ascending=False).apply(lambda x: f"{x:+.1%}"))