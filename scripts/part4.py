import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

conn = sqlite3.connect('fitbit_database.db')

# 1.fill in missing value of the table weight_log
query_weight = "SELECT * FROM weight_log"
cursor = conn.cursor()
cursor.execute(query_weight)
rows_weight = cursor.fetchall()
weight_df = pd.DataFrame(rows_weight, columns=[x[0] for x in cursor.description])

print("Missing values BEFORE resolution:")
print(weight_df[['WeightKg', 'BMI', 'Fat']].isnull().sum())

weight_df['CalculatedHeight'] = (weight_df['WeightKg'] / weight_df['BMI']) ** 0.5
weight_df['UserHeight'] = weight_df.groupby('Id')['CalculatedHeight'].transform('mean')
weight_df['UserHeight'] = weight_df['UserHeight'].fillna(weight_df['CalculatedHeight'].mean())
weight_df['BMI'] = weight_df['BMI'].fillna(weight_df['WeightKg'] / (weight_df['UserHeight'] ** 2))
weight_df['WeightKg'] = weight_df['WeightKg'].fillna(weight_df['BMI'] * (weight_df['UserHeight'] ** 2))


if 'Fat' in weight_df.columns:
    weight_df['Fat'] = weight_df['Fat'].fillna(weight_df.groupby('Id')['Fat'].transform('mean'))
    weight_df['Fat'] = weight_df['Fat'].fillna(weight_df['Fat'].mean())

print("\nMissing values AFTER resolution:")
print(weight_df[['WeightKg', 'BMI', 'Fat']].isnull().sum())
weight_df = weight_df.drop(columns=['CalculatedHeight', 'UserHeight'])

# 2.investigating relations between the various tables
query_activity = """
SELECT id, AVG(TotalSteps) AS AvgSteps, AVG(Calories) AS AvgCalories, AVG(SedentaryMinutes) AS AvgSedentary
From daily_activity
GROUP BY Id
"""

df_user_activity = pd.read_sql_query(query_activity, conn)

## Aggregate Sleep (Average minutes per sleep session per user). Counting all minute rows and dividing by the number of unique sleep sessions
query_sleep = """
SELECT 
    Id, 
    CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT logId) AS AvgSleepMinutes
FROM minute_sleep
GROUP BY Id;
"""
df_user_sleep = pd.read_sql_query(query_sleep, conn)

## Aggregate Weight & BMI (Average per user)
df_user_weight = weight_df
df_user_weight = weight_df.groupby('Id')['WeightKg'].mean().reset_index().rename(columns={'WeightKg': 'AvgWeight'})
df_user_weight = weight_df.groupby('Id')['BMI'].mean().reset_index().rename(columns={'BMI': 'AvgBMI'})

df_user_stats = pd.merge(df_user_activity, df_user_sleep, on='Id', how='inner')
df_user_stats = pd.merge(df_user_stats, df_user_weight, on='Id', how='inner')

print("\n--- Numerical Statistics per Individual (First 5 Users) ---")
print(df_user_stats.head())

print("\n--- Correlation Matrix ---")
correlation_matrix = df_user_stats.drop('Id', axis=1).corr()
print(correlation_matrix)

# This shows the strength of the linear relationships between all variables
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title("Correlation Heatmap: Average User Statistics")
plt.tight_layout()
plt.show()

# This graphically shows the scatter plots for every combination of variables
sns.pairplot(df_user_stats.drop('Id', axis=1), kind='reg', diag_kind='kde', plot_kws={'line_kws':{'color':'red'}}, corner=True)
plt.suptitle("Pairplot of User-Level Health Metrics", y=1.02)
plt.show()
print(weight_df[['Id', 'WeightKg', 'BMI', 'Fat']])

query_heart_rate = "SELECT * FROM heart_rate"
cursor = conn.cursor()
cursor.execute(query_heart_rate)
rows_heart_rate = cursor.fetchall()
heart_rate_df = pd.DataFrame(rows_heart_rate, columns=[x[0] for x in cursor.description])

heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"])
heart_rate_df['Hour'] = heart_rate_df['Time'].dt.floor('h')

heart_rate_hourly_df = (
    heart_rate_df.groupby(['Id', 'Hour'], as_index=False)['Value']
    .mean()
    .rename(columns={'Value': 'AvgValue'})
)

query_hourly_steps = "SELECT * FROM hourly_steps"
cursor = conn.cursor()
cursor.execute(query_hourly_steps)
rows_hourly_steps = cursor.fetchall()
hourly_steps_df = pd.DataFrame(rows_hourly_steps, columns=[x[0] for x in cursor.description])
hourly_steps_df = hourly_steps_df.rename(columns={'ActivityHour': 'Hour'})
hourly_steps_df["Hour"] = pd.to_datetime(hourly_steps_df["Hour"])

merged_df = pd.merge(
    hourly_steps_df,
    heart_rate_hourly_df,
    on=['Id', 'Hour'],
    how='inner'   # important: only matched rows
)

merged_df['StepBin'] = (merged_df['StepTotal'] // 500) * 500

plot_df = (
    merged_df
    .groupby('StepBin', as_index=False)['AvgValue']
    .mean()
)

for _, row in plot_df.iterrows():
    print(f"Steps: {int(row['StepBin'])} → Avg Heart Rate: {row['AvgValue']:.2f}")

plt.figure()
plt.plot(plot_df['StepBin'], plot_df['AvgValue'])

plt.xlabel("Steps per Hour")
plt.ylabel("Average Heart Rate")
plt.title("Steps vs Heart Rate")

plt.show()

conn.close()
