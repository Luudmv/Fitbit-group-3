# Fitbit Data Analysis & Dashboard

This repository contains a data analysis pipeline and a Streamlit-based dashboard designed to analyze health metrics from 33 respondents of a 2016 Fitbit survey. The project investigates relationships between physical activity, sleep quality, and environmental factors like weather.

## Table of Contents

* [Introduction]
* [Features]
* [Installation & Setup]
* [Data Sources]
* [Dashboard Pages]

---

## Introduction

This project analyses FitBit usage data from 33 respondents to an Amazon survey in 2016. The goal is to provide interactive visualizations and statistical insights into participants' daily activity, sleep patterns, heart rate, weight, and more — presented through a multi-page Streamlit dashboard.

## Features

* Individual user profiles — filter by user ID and date range to explore personal metrics
* Calories & steps tracking — daily calorie burn, step counts, and activity breakdowns
* OLS regression — steps-to-calories regression model with per-user effects (R² = 0.793)
* Sleep analysis — distribution of sleep durations, weekday vs. weekend comparisons, and individual timelines
* Weight & BMI monitoring — time-series plots with overweight threshold reference
* Heart rate & exercise intensity — high-resolution heart rate data combined with intensity metrics
* Time-of-day analysis — average steps, calories, and sleep broken down into 4-hour blocks
* Weather impact analysis — correlation between Chicago weather (rain, temperature) and activity levels
* Cross-metric correlation heatmap — steps, calories, sedentary time, and sleep

---

## ⚙️ Installation & Setup

To run the analysis and dashboard locally, follow these steps:

1. **Clone the Repository**:
```bash
git clone https://github.com/alanfrchen/Fitbit-group-3.git
cd Fitbit-group-3

```


2. **Install Dependencies**:
```bash
pip install pandas matplotlib seaborn sqlite3 statsmodels requests streamlit

```


3. **Running the Dashboard**:
```bash
streamlit run Overview.py

```

---

## Data Sources

The SQLite database (`fitbit_database.db`) contains the following tables:

| Table              | Description                                              |
|--------------------|----------------------------------------------------------|
| `daily_activity`   | Daily totals for steps, distance, calories, activity     |
| `heart_rate`       | Heart rate measured every 5 seconds                      |
| `hourly_calories`  | Calories burned per hour                                 |
| `hourly_intensity` | Exercise intensity per hour (total and average)          |
| `hourly_steps`     | Step count per hour                                      |
| `minute_sleep`     | Sleep state logged every minute                          |
| `weight_log`       | Weight, body fat %, and BMI measurements                 |

Weather data for Chicago (April 2016) was sourced from
[Visual Crossing](https://www.visualcrossing.com/weather-query-builder/).

---

## Dashboard Pages

### 🏠 Dashboard — General Overview
- Population-level statistics: average steps, calories, sleep, and distance
- Activity frequency by day of the week
- Correlation heatmap between key metrics
- Weather impact on high-intensity activity

### 👤 Individual
- Select a user by ID and date range
- Daily calories burned, step counts, activity breakdown
- Steps → Calories regression with per-user line
- Weight and BMI over time
- Heart rate and exercise intensity timeline

### 😴 Sleep
- Population sleep distribution histogram
- Average sleep by weekday (with weekend highlighting)
- OLS regression: sedentary minutes vs. sleep duration
- Q-Q plot for normality check of residuals
- Individual sleep timeline with 7-hour target reference

### 🕐 Time of Day
- Average steps, calories, and sleep broken into 4-hour blocks
  (0–4, 4–8, 8–12, 12–16, 16–20, 20–24)

### 📊 Data
- Raw table explorer for all database tables


---

## 👥 Contributors

Developed by Group 3.

* **Alan Chen**
* **Ruud**
* **Vigo**
* **Mustafa**

