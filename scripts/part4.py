import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# CONNECTION HELPERS

def get_connection(db_path: str = 'fitbit_database.db') -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def query_to_df(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=[x[0] for x in cursor.description])



# DATA PREPARATION FUNCTIONS

def prepare_user_stats(conn):
    query_activity = """
    SELECT Id, AVG(TotalSteps) AS AvgSteps, AVG(Calories) AS AvgCalories,
           AVG(SedentaryMinutes) AS AvgSedentary
    FROM daily_activity
    GROUP BY Id
    """

    query_sleep = """
    SELECT Id,
           CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT logId) AS AvgSleepMinutes
    FROM minute_sleep
    GROUP BY Id
    """

    df_activity = query_to_df(conn, query_activity)
    df_sleep = query_to_df(conn, query_sleep)

    df = pd.merge(df_activity, df_sleep, on='Id', how='inner')
    return df


def prepare_hourly_merged(conn):
    heart_rate = query_to_df(conn, "SELECT * FROM heart_rate")
    steps = query_to_df(conn, "SELECT * FROM hourly_steps")

    heart_rate["Time"] = pd.to_datetime(heart_rate["Time"])
    heart_rate["Hour"] = heart_rate["Time"].dt.floor('h')

    heart_rate = (
        heart_rate.groupby(['Id', 'Hour'], as_index=False)['Value']
        .mean()
        .rename(columns={'Value': 'AvgHeartRate'})
    )

    steps = steps.rename(columns={'ActivityHour': 'Hour'})
    steps["Hour"] = pd.to_datetime(steps["Hour"])

    merged = pd.merge(steps, heart_rate, on=['Id', 'Hour'], how='inner')
    return merged



# PLOTTING FUNCTIONS

def plot_correlation_heatmap(df):
    corr = df.drop('Id', axis=1).corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()


def plot_pairplot(df):
    sns.pairplot(
        df.drop('Id', axis=1),
        kind='reg',
        diag_kind='kde',
        plot_kws={'line_kws': {'color': 'red'}},
        corner=True
    )
    plt.suptitle("Pairplot of User Metrics", y=1.02)
    plt.show()


def plot_steps_vs_heart_rate(merged_df):
    merged_df['StepBin'] = (merged_df['StepTotal'] // 500) * 500

    plot_df = (
        merged_df.groupby('StepBin', as_index=False)['AvgHeartRate']
        .mean()
    )

    plt.figure()
    plt.plot(plot_df['StepBin'], plot_df['AvgHeartRate'])
    plt.xlabel("Steps per Hour")
    plt.ylabel("Average Heart Rate")
    plt.title("Steps vs Heart Rate")
    plt.show()


def plot_steps_vs_heart_rate_regression(merged_df):
    sns.regplot(
        data=merged_df,
        x='StepTotal',
        y='AvgHeartRate',
        scatter_kws={'alpha': 0.3}
    )
    plt.title("Steps vs Heart Rate (Regression)")
    plt.show()


def plot_hourly_steps_distribution(conn):
    steps = query_to_df(conn, "SELECT * FROM hourly_steps")
    steps["ActivityHour"] = pd.to_datetime(steps["ActivityHour"])
    steps['HourOfDay'] = steps["ActivityHour"].dt.hour

    sns.boxplot(data=steps, x='HourOfDay', y='StepTotal')
    plt.title("Steps Distribution by Hour")
    plt.show()


def plot_heart_rate_by_hour(conn):
    heart_rate = query_to_df(conn, "SELECT * FROM heart_rate")
    heart_rate["Time"] = pd.to_datetime(heart_rate["Time"])
    heart_rate['HourOfDay'] = heart_rate["Time"].dt.hour

    sns.lineplot(data=heart_rate, x='HourOfDay', y='Value')
    plt.title("Heart Rate by Hour")
    plt.show()


# MAIN EXECUTION

if __name__ == "__main__":
    conn = get_connection()

    # Prepare datasets
    df_user_stats = prepare_user_stats(conn)
    merged_df = prepare_hourly_merged(conn)

    # Generate plots
    plot_correlation_heatmap(df_user_stats)
    plot_pairplot(df_user_stats)
    plot_steps_vs_heart_rate(merged_df)
    plot_steps_vs_heart_rate_regression(merged_df)
    plot_hourly_steps_distribution(conn)
    plot_heart_rate_by_hour(conn)

    conn.close()
