import sqlite3
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import json
import urllib.request
import ssl



# Get sleep duration minutes
conn = sqlite3.connect('fitbit_database.db')

query = f"""
SELECT Id, logId, DATE(date) AS SleepDate, COUNT(*) AS sleep_duration_min
FROM minute_sleep
GROUP BY logId
"""

cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()
sleep_duration_df = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])
print(sleep_duration_df.head())

# active minutes on a day and the minutes of sleep regression 
query_activity = """
SELECT Id, ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes
FROM daily_activity
"""
cursor.execute(query_activity)
rows_of_activity = cursor.fetchall()
daily_activity_df = pd.DataFrame(rows_of_activity, columns = [x[0] for x in cursor.description])

daily_activity_df['TotalActiveMinutes'] = (
    daily_activity_df['VeryActiveMinutes'] +
    daily_activity_df['FairlyActiveMinutes'] +
    daily_activity_df['LightlyActiveMinutes'] 
)
print(daily_activity_df.head())

df_analysis_0 = pd.merge(sleep_duration_df, daily_activity_df,
                         left_on=['Id', 'SleepDate'],right_on=['Id', 'ActivityDate'])

X = df_analysis_0['TotalActiveMinutes']
y = df_analysis_0['sleep_duration_min']
X = sm.add_constant(X) 

model = sm.OLS(y, X).fit()
print(model.summary())

# relationship between sedentary activity and the sleep duration (a linear regression)

query_sedentary = """
SELECT Id, ActivityDate, SedentaryMinutes
FROM daily_activity
"""

cursor.execute(query_sedentary)
rows_sedentary = cursor.fetchall()
sedentary_df = pd.DataFrame(rows_sedentary, columns = [x[0] for x in cursor.description])
sedentary_df['ActivityDate'] = pd.to_datetime(sedentary_df['ActivityDate'])
query_sleep_with_date = """
SELECT Id, logId, DATE(date) AS SleepDate, COUNT(*) AS sleep_duration_min
FROM minute_sleep
GROUP BY logId
"""
sleep_with_date = pd.read_sql_query(query_sleep_with_date, conn)
sleep_with_date['SleepDate'] = pd.to_datetime(sleep_with_date['SleepDate'])

df_analysis_1 = pd.merge(sleep_with_date,sedentary_df,
    left_on=['Id', 'SleepDate'],
    right_on=['Id', 'ActivityDate'],
    how='inner'
)

X = df_analysis_1['SedentaryMinutes']
y = df_analysis_1['sleep_duration_min']
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())

residuals = model.resid
fig = sm.qqplot(residuals, line = 's')
plt.title("Q-Q Plot to Verify Normal Distribution of Errors")
plt.show()

# steps, calories burnt and minutes of sleep taken in blocks
def blocks_and_plots(table_name, value_col, time_col, label):
    query = f"SELECT {time_col}, {value_col} FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    
    df[time_col] = pd.to_datetime(df[time_col])
    df['hour'] = df[time_col].dt.hour
    
    bins = [0, 4, 8, 12, 16, 20, 24]
    labels = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']
    df['time_block'] = pd.cut(df['hour'], bins = bins, labels = labels, right = False)
    
    avg_block = df.groupby('time_block')[value_col].mean().reset_index()
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=avg_block, x='time_block', y=value_col, palette='viridis')
    plt.title(f'Average {label} per 4-Hour Block')
    plt.ylabel(f'Average {label}')
    plt.xlabel('Time Block (Hours)')
    plt.show()
    
blocks_and_plots('hourly_steps', 'StepTotal', 'ActivityHour', 'Steps')
blocks_and_plots('hourly_calories', 'Calories', 'ActivityHour', 'Calories')
# blocks_and_plots('minute_sleep', '')

query_sleep = "SELECT date FROM minute_sleep"
df_sleep = pd.read_sql_query(query_sleep, conn)
df_sleep['date'] = pd.to_datetime(df_sleep['date'])
df_sleep['hour'] = df_sleep['date'].dt.hour
df_sleep['time_block'] = pd.cut(df_sleep['hour'], bins=[0,4,8,12,16,20,24], 
                                labels=['0-4','4-8','8-12','12-16','16-20','20-24'], right=False)

sleep_stats = df_sleep.groupby(['time_block']).size() / df_sleep['date'].dt.date.nunique()
sleep_stats.plot(kind='bar', color='skyblue', title='Average Sleep Minutes per 4-Hour Block')
plt.show()

# figure of heart rate and total intensity of the exercise taken
def plot_individual_activity(user_id):
    hr_query = f"SELECT Time, Value From heart_rate Where Id = '{user_id}'"
    df_hr = pd.read_sql_query(hr_query, conn)
    df_hr['Time'] = pd.to_datetime(df_hr['Time'])
    
    int_query = f"SELECT ActivityHour, TotalIntensity FROM hourly_intensity WHERE Id = '{user_id}'"
    df_int = pd.read_sql_query(int_query, conn)
    df_int['ActivityHour'] = pd.to_datetime(df_int['ActivityHour'])
    
    if df_hr.empty or df_int.empty:
        print(f"No data found for ID: {user_id}")
        return
    
    fig, ax1 = plt.subplots(figsize = (12, 6))
    ax1.plot(df_hr['Time'], df_hr['Value'], color = 'red', alpha = 0.5, label = 'Hear rate')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Heart Rate', color = 'red')
    ax1.tick_params(axis = 'y', labelcolor = 'red')
    
    ax2 = ax1.twinx()
    ax2.step(df_int['ActivityHour'], df_int['TotalIntensity'], where='post', color='blue', linewidth=2, label='Total Intensity')
    ax2.set_ylabel('Total Intensity', color = 'blue')
    ax2.tick_params(axis = 'y', labelcolor = 'blue')
    
    plt.title(f'Activity Analysis for User: {user_id}')
    fig.tight_layout()
    
    return fig

my_fig = plot_individual_activity(2022484408)
plt.show()

#relation between weather factors (precipation, temperature and the activity of the individuals)

api_key = 'XBBJ63DAZ6XASGHZXAJY6BKJV'
location = 'Chicago,IL'
unit_group = 'metric'
content_type = 'json'
include = 'days'

start_date = '2016-03-25'
end_date = '2016-04-15'

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


# Construct the API URL with a date range
url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}?unitGroup={unit_group}&contentType={content_type}&include={include}&key={api_key}'

# Make the request
with urllib.request.urlopen(url, context=ssl_context) as response:
    # Read and decode the JSON data
    weather_data = json.loads(response.read().decode())
    # Output the JSON response

days_data = weather_data['days']
weather_df = pd.DataFrame(days_data)
weather_df = weather_df[['datetime', 'temp', 'precip']]
weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])

print(weather_df.head())

query_of_activity = """
SELECT ActivityDate, TotalSteps, VeryActiveMinutes
FROM daily_activity
"""
cursor.execute(query_of_activity)
rows_activity = cursor.fetchall()
activity_df = pd.DataFrame(rows_activity, columns = [x[0] for x in cursor.description])

activity_df['ActivityDate'] = pd.to_datetime(activity_df['ActivityDate'])
merged_df = pd.merge(activity_df, weather_df, left_on='ActivityDate', right_on='datetime')

plt.figure(figsize = (10, 6))
sns.regplot(data=merged_df, x='temp', y='TotalSteps', order=2, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
plt.title('Relationship between Temperature and Daily Steps in Chicago')
plt.xlabel('Average Daily Temperature (°C)')
plt.ylabel('Total Steps')
plt.show()

plt.figure(figsize=(10, 6))
merged_df['is_raining'] = merged_df['precip'] > 0
sns.boxplot(data=merged_df, x='is_raining', y='VeryActiveMinutes')
plt.title('Impact of Rain on High-Intensity Activity')
plt.xticks([0, 1], ['No Rain', 'Rain'])
plt.show()

conn.close()
