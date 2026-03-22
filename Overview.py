import json
import ssl
import urllib.request
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import data

st.set_page_config(
    page_title="FitBit Analytics",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="auto",
)

st.sidebar.markdown("📊 **Overview**")
st.sidebar.page_link("pages/1_individual.py", label="👤 Individual")
st.sidebar.page_link("pages/2_sleep.py", label="😴 Sleep Analysis")
st.sidebar.page_link("pages/3_time_of_day_blocks.py", label="🕐 Time of Day")

st.title("📊 General statistics")
st.logo(image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Fitbit_logo16.svg/3840px-Fitbit_logo16.svg.png", size="large")

# overview metrics
stats = data.get_overview_stats()
users = data.get_user_classes()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Participants in survey", int(stats["total_users"]), border=True)
col2.metric("Average daily steps", int(stats["avg_steps"]), border=True)
col3.metric("Average daily calories", int(stats["avg_calories"]), border=True)
col4.metric("Average daily distance", f"{stats['avg_distance']:.1f} km", border=True)
col5.metric("Average very active mins", f"{int(stats['avg_very_active'])} min", border=True)

# distance bar chart  and pie chart
st.subheader("Distance and user classification")
column1, column2 = st.columns([2, 1])
distance = data.get_total_distance_per_user()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(distance["Id"].astype(str), distance["TotalDistance"], color="#52dee3")
ax.set_xlabel("User ID", fontsize=9)
ax.set_ylabel("Total distance (km)", fontsize=9)
ax.set_title("Total distance registered per user", fontweight="bold")
ax.tick_params(axis="x", rotation=90, labelsize=7)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
column1.pyplot(fig)
plt.close(fig)

class_counts = users["Class"].value_counts()
fig, ax = plt.subplots(figsize=(5, 5))
wedge_colors = {"Light": "#ad2bab", "Moderate": "#52dee3", "Heavy": "#e35752"}
ax.pie(class_counts.values, labels=class_counts.index,
       colors=[wedge_colors[c] for c in class_counts.index], autopct="%.0f%%")
ax.set_title("User classification", fontweight="bold")
column2.pyplot(fig)
plt.close(fig)

# activity patterns
st.subheader("Activity patterns")
col1, col2 = st.columns(2)
wday = data.get_workout_frequency_by_weekday()
fig, ax = plt.subplots(figsize=(6, 3.5))
bar_colors = ["#e94560" if day in ["Wednesday", "Thursday"] else "#52dee3" for day in wday["Weekday"]]
ax.bar(wday["Weekday"], wday["Count"], color=bar_colors, edgecolor="none")
ax.set_title("Workout frequency by day of week", fontsize=11, fontweight="bold")
ax.set_ylabel("Number of entries")
ax.tick_params(axis="x", rotation=30)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
col1.pyplot(fig)
plt.close(fig)

avgs = data.get_avg_metrics_by_weekday()
fig, ax1 = plt.subplots(figsize=(6, 3.5))
ax2 = ax1.twinx()
ax1.bar(avgs["Weekday"], avgs["TotalSteps"], color="#52dee3", label="Avg Steps")
ax2.plot(avgs["Weekday"], avgs["Calories"], color="#e94560", marker="x", linewidth=1, label="Avg Calories")
ax1.set_ylabel("Avg Steps", color="#1a1a2e", fontsize=12)
ax2.set_ylabel("Avg Calories", color="#e94560", fontsize=12)
ax1.set_title("Avg steps & calories by weekday", fontweight="bold")
ax1.tick_params(axis="x", rotation=30)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=7)
ax1.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
col2.pyplot(fig)
plt.close(fig)

@st.cache_data
def get_weather():
    api_key    = 'NVVCJ7HHKQWNTV926VHHETWYZ'
    location   = 'Chicago,IL'
    start_date = '2016-03-25'
    end_date   = '2016-05-12'

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    url = (f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/"
           f"timeline/{location}/{start_date}/{end_date}"
           f"?unitGroup=metric&contentType=json&include=days&key={api_key}")

    with urllib.request.urlopen(url, context=ssl_context) as response:
        weather_data = json.loads(response.read().decode())

    df = pd.DataFrame(weather_data["days"])[["datetime", "temp", "precip"]]
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

weather_df = get_weather()
activity_df = data.get_steps_and_active_minutes()
activity_df["ActivityDate"] = pd.to_datetime(
    activity_df["ActivityDate"], infer_datetime_format=True
).dt.normalize()

merged_df = pd.merge(activity_df, weather_df, left_on="ActivityDate", right_on="datetime")
merged_df["is_raining"] = merged_df["precip"] > 0

st.subheader("Insights")
col1, col2 = st.columns(2)

# heatmap
df_corr = data.get_user_stats_merged()
corr = df_corr.drop("Id", axis=1).corr()
corr.columns = ["Avg Steps", "Avg Calories", "Avg Sedentary", "Avg Sleep"]
corr.index   = ["Avg Steps", "Avg Calories", "Avg Sedentary", "Avg Sleep"]
fig, ax = plt.subplots(figsize=(5, 3.5))
im = ax.imshow(corr, cmap="cool", vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=30, ha="right", fontsize=8)
ax.set_yticklabels(corr.index, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr.columns)):
        val = corr.iloc[i, j]
        color = "white" if abs(val) > 0.5 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, fontweight="bold", color=color)
ax.set_title("Correlation between user metrics", fontweight="bold")
fig.tight_layout()
col1.pyplot(fig)
plt.close(fig)

# rain vs activity
rain_summary = merged_df.groupby("is_raining")["VeryActiveMinutes"].agg(["mean", "sem"]).reset_index()
fig, ax = plt.subplots(figsize=(5, 3.5))
bars = ax.bar(["No Rain", "Rain"], rain_summary["mean"], color=["#52dee3", "#0f3460"], alpha=0.85)
ax.errorbar(["No Rain", "Rain"], rain_summary["mean"], yerr=rain_summary["sem"],
            fmt="none", color="#e94560", capsize=5, linewidth=1.5)
ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=9)
ax.set_ylabel("Avg Very Active Minutes")
ax.set_title("Impact of Rain on High-Intensity Activity", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
no_rain_mean = rain_summary.loc[rain_summary["is_raining"] == False, "mean"].values[0]
rain_mean    = rain_summary.loc[rain_summary["is_raining"] == True,  "mean"].values[0]
pct_diff = ((rain_mean - no_rain_mean) / no_rain_mean) * 100
ax.text(0.5, 0.92, f"{pct_diff:+.1f}% on rainy days",
        transform=ax.transAxes, ha="center", fontsize=9, color="#e94560")
fig.tight_layout()
col2.pyplot(fig)
plt.close(fig)
