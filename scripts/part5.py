import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Fitbit Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_db_connection():
    return sqlite3.connect('fitbit_database.db')

# DATA LOADING FUNCTIONS
@st.cache_data
def load_general_stats():
    conn = get_db_connection()
    df_activity = pd.read_sql("""
        SELECT Id, ActivityDate, TotalSteps, TotalDistance, Calories,
               VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes, SedentaryMinutes
        FROM daily_activity
    """, conn)
    conn.close()
    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate'])
    return df_activity

@st.cache_data
def get_user_list():
    conn = get_db_connection()
    ids = pd.read_sql("SELECT DISTINCT Id FROM daily_activity ORDER BY Id", conn)
    conn.close()
    return ids['Id'].tolist()

@st.cache_data
def load_sleep_data():
    conn = get_db_connection()
    sleep_df = pd.read_sql("""
        SELECT Id, logId, COUNT(*) as sleep_duration_min 
        FROM minute_sleep 
        GROUP BY Id, logId
    """, conn)
    conn.close()
    return sleep_df

# SIDEBAR NAVIGATION
st.sidebar.title("📊 Fitbit Research Dashboard")
page = st.sidebar.radio("Navigation", [
    "🏠 Project Overview", 
    "👤 Individual Analytics", 
    "😴 Sleep Analysis"
])

# PAGE 1: PROJECT OVERVIEW
if page == "🏠 Project Overview":
    st.title("🏃 Fitbit Research - General Statistics")
    
    df = load_general_stats()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Participants", df['Id'].nunique())
    col2.metric("Observations", len(df))
    col3.metric("Avg Steps", f"{int(df['TotalSteps'].mean()):,}")
    col4.metric("Avg Calories", f"{int(df['Calories'].mean()):,}")
    
    # Visualizations
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Daily Steps Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df['TotalSteps'], bins=50, color='#00CC96', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Total Steps')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)
        
        st.subheader("Steps Statistics")
        st.dataframe(df['TotalSteps'].describe())
    
    with col_right:
        st.subheader("Calories Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df['Calories'], bins=50, color='#FF6B6B', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Calories')
        st.pyplot(fig)
        
        st.subheader("Activity Minutes")
        activity_means = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 
                            'LightlyActiveMinutes', 'SedentaryMinutes']].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(activity_means.index, activity_means.values, 
               color=['#e74c3c', '#f39c12', '#3498db', '#95a5a6'])
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

# PAGE 2: INDIVIDUAL ANALYTICS
elif page == "👤 Individual Analytics":
    st.title("👤 Individual Participant Report")
    
    user_ids = get_user_list()
    selected_id = st.sidebar.selectbox("Select Participant ID", user_ids)
    
    # Time filter
    st.sidebar.subheader("⏰ Time Filter")
    date_range = st.sidebar.date_input("Select Date Range", value=[])
    
    # Load data
    conn = get_db_connection()
    df_user = pd.read_sql(f"SELECT * FROM daily_activity WHERE Id = {selected_id}", conn)
    conn.close()
    df_user['ActivityDate'] = pd.to_datetime(df_user['ActivityDate'])
    
    # Apply filter
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_user = df_user[(df_user['ActivityDate'] >= start) & (df_user['ActivityDate'] <= end)]
    
    st.markdown(f"### User: **{selected_id}**")
    
    # User KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Days Tracked", len(df_user))
    col2.metric("Avg Steps", f"{int(df_user['TotalSteps'].mean()):,}")
    col3.metric("Avg Distance", f"{df_user['TotalDistance'].mean():.2f} km")
    col4.metric("Avg Calories", f"{int(df_user['Calories'].mean()):,}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "📊 Activity Breakdown", "📋 Raw Data"])
    
    with tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Steps Trend")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_user['ActivityDate'], df_user['TotalSteps'], 
                   marker='o', linewidth=2, color='#3498db')
            ax.set_xlabel('Date')
            ax.set_ylabel('Steps')
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        
        with col_right:
            st.subheader("Calories Trend")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_user['ActivityDate'], df_user['Calories'], 
                   marker='s', linewidth=2, color='#e74c3c')
            ax.set_xlabel('Date')
            ax.set_ylabel('Calories')
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
    
    with tab2:
        st.subheader("Activity Distribution")
        avg_activity = df_user[['VeryActiveMinutes', 'FairlyActiveMinutes', 
                               'LightlyActiveMinutes', 'SedentaryMinutes']].mean()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(avg_activity, labels=avg_activity.index, autopct='%1.1f%%',
               colors=['#e74c3c', '#f39c12', '#3498db', '#95a5a6'])
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Statistical Summary")
        st.dataframe(df_user.describe().T)

# PAGE 3: SLEEP ANALYSIS
elif page == "😴 Sleep Analysis":
    st.title("😴 Sleep Duration Analysis")
    st.markdown("**Does physical activity affect sleep duration?**")
    
    df_activity = load_general_stats()
    df_sleep = load_sleep_data()
    
    # Calculate total active minutes
    df_activity['TotalActiveMinutes'] = (df_activity['VeryActiveMinutes'] + 
                                        df_activity['FairlyActiveMinutes'] + 
                                        df_activity['LightlyActiveMinutes'])
    
    # Aggregate sleep by user
    sleep_avg = df_sleep.groupby('Id')['sleep_duration_min'].mean().reset_index()
    sleep_avg.columns = ['Id', 'AvgSleepMinutes']
    
    # Merge
    df_merged = pd.merge(df_activity, sleep_avg, on='Id', how='inner')
    
    # Sidebar controls
    var_to_check = st.sidebar.selectbox(
        "Select Variable:",
        ["TotalActiveMinutes", "VeryActiveMinutes", "FairlyActiveMinutes", 
         "LightlyActiveMinutes", "SedentaryMinutes", "TotalSteps"]
    )
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader(f"{var_to_check} vs Sleep Duration")
        
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.scatter(df_merged[var_to_check], df_merged['AvgSleepMinutes'], 
                  alpha=0.6, s=80, color='#9b59b6')
        
        # Trend line
        z = np.polyfit(df_merged[var_to_check].dropna(), 
                      df_merged['AvgSleepMinutes'].dropna(), 1)
        p = np.poly1d(z)
        ax.plot(df_merged[var_to_check], p(df_merged[var_to_check]), 
               "r--", linewidth=2.5, label=f'Trend (slope={z[0]:.3f})')
        
        ax.set_xlabel(var_to_check)
        ax.set_ylabel('Sleep Duration (minutes)')
        ax.legend()
        st.pyplot(fig)
    
    with col_right:
        st.subheader("Correlation Analysis")
        
        correlation = df_merged[var_to_check].corr(df_merged['AvgSleepMinutes'])
        st.metric("Pearson Correlation", f"{correlation:.3f}")
        
        # Regression
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df_merged[var_to_check].dropna(), 
            df_merged['AvgSleepMinutes'].dropna()
        )
        
        st.write(f"**R-squared:** {r_value**2:.3f}")
        st.write(f"**P-value:** {p_value:.2e}")
        
        if p_value < 0.05:
            st.success("✅ Statistically significant")
        else:
            st.warning("⚠️ Not statistically significant")

st.sidebar.markdown("---")
st.sidebar.info("Fitbit Research Dashboard v1.0")