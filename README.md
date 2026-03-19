# 🏃 Fitbit Data Analysis & Dashboard

This repository contains a data analysis pipeline and a Streamlit-based dashboard designed to analyze health metrics from 33 respondents of a 2016 Fitbit survey. The project investigates relationships between physical activity, sleep quality, and environmental factors like weather .

## 📋 Table of Contents

* [Introduction]
* [Database Schema]
* [Installation & Setup]
* [Analysis Features]
* [Dashboard Requirements]
* [Usage]

---

## 📖 Introduction

The goal of this project is to provide business analysts and survey participants with a tool to explore health trends. The study uses usage data submitted via an Amazon survey to track calories, steps, heart rate, and sleep patterns.

## 🗄️ Database Schema

The analysis utilizes the `fitbit_database.db` SQLite database, which includes the following tables :

* 
**`daily_activity`**: Daily statistics for steps, calories, and distances.


* 
**`heart_rate`**: Measurements taken every 5 seconds.


* 
**`minute_sleep`**: Minute-by-minute sleep state logs.


* 
**`weight_log`**: Logs for weight, BMI, and body fat percentage.


* 
**`hourly_calories`, `hourly_steps`, `hourly_intensity**`: Temporal data for granular analysis .



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


3. **Database File**:
Ensure `fitbit_database.db` is located in the root directory of the project.



---

## 🔬 Analysis Features

The `part3_stu.py` script performs several statistical investigations:

* 
**Sleep Duration Regression**: Analyzes the relationship between active minutes (Very, Fairly, and Lightly active) and sleep duration.


* 
**Sedentary vs. Sleep**: A linear regression investigating how sedentary time affects rest, including Q-Q plots to verify normal distribution of errors.


* 
**4-Hour Time Blocks**: Aggregates activity into 4-hour windows (0-4, 4-8, etc.) to visualize daily patterns.


* 
**Weather Integration**: Uses the **Visual Crossing WebAPI** to correlate Chicago weather (temperature/precipitation) with participant activity levels .


* 
**Weight Data Wrangling**: Resolves missing BMI and weight values using the $kg/m^{2}$ formula instead of deleting records.



---

## 📊 Dashboard Requirements

The Streamlit dashboard (`dashboard.py`) meets the following criteria :

* 
**Opening Page**: General research statistics with both numerical and graphical summaries.


* 
**Individual Drill-down**: A sidebar selector to view detailed statistics for a specific Participant ID.


* 
**Time Components**: Filters for specific date ranges and time-of-day analysis.


* 
**Sleep Analysis**: A dedicated section to deduce which variables (like sedentary time or activity) affect sleep duration.



---

## 🚀 Usage

### To run the Analysis Script:

```bash
python scripts/part3_stu.py

```

### To launch the Dashboard:

```bash
streamlit run scripts/dashboard.py

```

---

## 👥 Contributors

Developed by Group 3.

* **Alan Chen**
* **Ruud**
* **Figo**
