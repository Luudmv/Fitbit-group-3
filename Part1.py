from scipy.stats import bernoulli
import matplotlib.pyplot as plt
import math
import pandas as pd
from datetime import timedelta

database = pd.read_csv("daily_acivity.csv")
unique_users = database["Id"].nunique()
print("Number of unique users:", unique_users)

total_distance_by_user = database.groupby("Id", as_index=False)["TotalDistance"].sum()
print(total_distance_by_user)

# plt.figure(figsize=(10, 5))
# plt.bar(
#     total_distance_by_user["Id"].astype(str),
#     total_distance_by_user["TotalDistance"]
# )

# plt.xlabel("User Id")
# plt.ylabel("Total Distance")
# plt.title("Total Distance per User")
# plt.xticks(rotation=90)
# plt.tight_layout()
# plt.show()

def user_friendly(user_id):
    # dates_of_this_user = database.loc[database["Id"] == user_id, "ActivityDate"]
    plt.plot(database.loc[database["Id"] == user_id, "ActivityDate"], database.loc[database["Id"] == user_id, "Calories"])
    plt.xlabel("Date")
    plt.ylabel("Calories burnt")
    plt.title(f"Calories burnt per day by user {user_id}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def lazy_sunday():
    ids = database["Id"].unique()
    lasts = []
    for id in ids:
        last = database.loc[database["Id"] == id, "Calories"].to_list()[-1]
        lasts.append(last)
        print(last)
    lasts_averages = sum(lasts)/len(lasts) 
    plt.figure(figsize=(10,5))
    plt.bar(ids.astype(str), lasts)
    plt.axhline(y=lasts_averages, color='red', linestyle=':', label = f"average calories burnt last day ({round(lasts_averages,1)})")
    plt.xlabel("User Id from de pauper luie mensjes")
    plt.ylabel("Calories burnt")
    plt.title("Calories burnt last day")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.legend()
    plt.show()
    # plt.plot(last_values["Id"].astype(str), last_values["Calories"], marker="o")
# user_friendly(1927972279)
lazy_sunday()