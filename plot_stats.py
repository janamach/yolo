import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import sys
import gc
import os
import numpy as np

input_file = "~/data/stats20240927.csv"

df = pd.read_csv(input_file)
print(df)

# Normalize the data to each day and group. First, group by month, day and group
for slice, sdf in df.groupby(["month", "day", "group"]):
    print(slice)
    # Add average_movement column to get total movement per day
    total_movement = sdf["average_movement"].sum()
    sdf["movement_normalized"] = sdf["average_movement"] / total_movement
    print(sdf)
    df.loc[sdf.index, "movement_normalized"] = sdf["movement_normalized"]

# # Plot catplot, 
# sns.catplot(data=df, x="time", y="movement_normalized", hue="group", kind="bar", col="month")
# plt.show()
# plt.close()

stats_df = pd.DataFrame(columns=["month", "time", "group", "feeding_avg", "feeding_std", "movement_avg", "movement_std"])
for slice, sdf in df.groupby(["month", "time", "group"]):
    print(slice)
    feeding_avg = sdf["feeding_mean"].mean()
    feeding_std = sdf["feeding_mean"].std()
    #movement_avg = sdf["average_movement"].mean()
    #movement_std = sdf["average_movement"].std()
    movement_avg = sdf["movement_normalized"].mean()
    movement_std = sdf["movement_normalized"].std()
    
    print(feeding_avg, feeding_std, movement_avg, movement_std)
    # concatinae to stats_df
    stats_df = pd.concat([stats_df, pd.DataFrame([[slice[0], slice[1], slice[2], feeding_avg, feeding_std, movement_avg, movement_std]], columns=stats_df.columns)], axis=0, ignore_index=True)
    print(stats_df)

Jul_B1 = stats_df[(stats_df["month"] == "Jul") & (stats_df["group"] == "Group 1")]
Aug_B1 = stats_df[(stats_df["month"] == "Aug") & (stats_df["group"] == "Group 1")]
Jul_B2 = stats_df[(stats_df["month"] == "Jul") & (stats_df["group"] == "Group 2")]
Aug_B2 = stats_df[(stats_df["month"] == "Aug") & (stats_df["group"] == "Group 2")]
# Plot lineplot
sns.lineplot(data=Jul_B1, x="time", y="movement_avg", hue="group", color="blue")
sns.lineplot(data=Jul_B2, x="time", y="movement_avg", hue="group", color="red")
# Plot std as shaded area
plt.fill_between(Jul_B1["time"], Jul_B1["movement_avg"] - Jul_B1["movement_std"], Jul_B1["movement_avg"] + Jul_B1["movement_std"], color='blue', alpha=0.2)
plt.fill_between(Jul_B2["time"], Jul_B2["movement_avg"] - Jul_B2["movement_std"], Jul_B2["movement_avg"] + Jul_B2["movement_std"], color='red', alpha=0.2)

#sns.lineplot(data=Aug_B1, x="time", y="movement_avg", hue="group", color="red")
#plt.fill_between(Aug_B1["time"], Aug_B1["movement_avg"] - Aug_B1["movement_std"], Aug_B1["movement_avg"] + Aug_B1["movement_std"], color='red', alpha=0.2)
plt.show()
plt.close()

sns.lineplot(data=Aug_B1, x="time", y="movement_avg", hue="group", color="blue")
sns.lineplot(data=Aug_B2, x="time", y="movement_avg", hue="group", color="red")
# Plot std as shaded area
plt.fill_between(Aug_B1["time"], Aug_B1["movement_avg"] - Aug_B1["movement_std"], Aug_B1["movement_avg"] + Aug_B1["movement_std"], color='blue', alpha=0.2)
plt.fill_between(Aug_B2["time"], Aug_B2["movement_avg"] - Aug_B2["movement_std"], Aug_B2["movement_avg"] + Aug_B2["movement_std"], color='red', alpha=0.2)
#sns.lineplot(data=Aug_B1, x="time", y="movement_avg", hue="group", color="red")
#plt.fill_between(Aug_B1["time"], Aug_B1["movement_avg"] - Aug_B1["movement_std"], Aug_B1["movement_avg"] + Aug_B1["movement_std"], color='red', alpha=0.2)
plt.show()