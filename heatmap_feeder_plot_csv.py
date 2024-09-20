import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import sys

fps=30

imput_file = sys.argv[1]
#input_file='B1_20240810_070001.mp4.csv'
# Read the CSV file
df = pd.read_csv(imput_file)

# Calculate total length of the video by subtracting the first frame from the last frame
# and dividing by the fps
total_length_sec = (df['frame'].iloc[-1] - df['frame'].iloc[0]) / fps
print(total_length_sec)

# print head of the dataframe
print(df.head())

# make a separate df with two classes 'bird' and 'white' called df2
bdf = df[(df['class'] == 'bird') | (df['class'] == 'white')]
df = df[(df['class'] != 'bird') & (df['class'] != 'white')]
# print head of the dataframe
print(bdf.head())
print(df.head())

# The data in X1, Y1, X2, Y2, are for the bounding box. We can calculate the width and height of the bounding box
df['width'] = df['X2'] - df['X1']
df['height'] = df['Y2'] - df['Y1']

# Print the length of the dataframe
print(len(df))

# Create ax and figure with fixes size
fig, ax = plt.subplots(figsize=(6, 4))

# plot the x_center, y_center of bdf as a 2d histogram
hb = ax.hexbin(bdf['X1'], bdf['Y1'], gridsize=80, cmap='inferno', bins='log')
# Set background color to the lowest value of the hexbin
ax.set_facecolor(plt.cm.inferno(0))
# plot the rectangles with width and height at x_center, y_center position
for classes, cdf in df.groupby('class'):
    mean_x1 = cdf['X1'].mean()
    mean_y1 = cdf['Y1'].mean()
    mean_x2 = cdf['X2'].mean()
    mean_y2 = cdf['Y2'].mean()
    mean_y = cdf['center_y'].mean()
    mean_x = cdf['center_x'].mean()
    # Store the centroid of the seeds as x_seeds and y_seeds
    if classes == 'seeds':
        x_seeds = mean_x
        y_seeds = mean_y
    # plot the rectangles with width and height at x_center, y_center position
    plt.plot([mean_x1, mean_x2], [mean_y1, mean_y1], color='red', linewidth=2)
    plt.plot([mean_x1, mean_x2], [mean_y2, mean_y2], color='red', linewidth=2)
    plt.plot([mean_x1, mean_x1], [mean_y1, mean_y2], color='red', linewidth=2)
    plt.plot([mean_x2, mean_x2], [mean_y1, mean_y2], color='red', linewidth=2)


# plot dimentions 2304x1296
plt.xlim(0, 2304)
plt.ylim(0, 1296)
plt.gca().invert_yaxis()

plt.savefig(imput_file + '.png')
plt.close()

# Plot time series of the distance between the centroids of birds to
# the centroid of seeds

# Calculate distance between x_center and y_center in bdf to
# x_seeds and y_seeds
bdf['distance'] = ((bdf['center_x'] - x_seeds) ** 2 + (bdf['center_y'] - y_seeds) ** 2) ** 0.5
# Print mean and max distance
print(bdf['distance'].min())
print(bdf['distance'].max())

# Only take frames where the distance is below 300
bdf2 = bdf[bdf['distance'] < 200]

# Calculate the average count of unique ID's in bdf2 per frame and store it in avg_ids
unique_ids = bdf2.groupby('frame')['ID'].nunique()
# Divide frame by fps to get the time in minutes
unique_ids.index = unique_ids.index / fps / 60
print(unique_ids)
last_minute=unique_ids.index[-1]

# Create ax and figure with fixes size
fig, ax = plt.subplots(figsize=(8, 2))

# Use lineplot to plot the unique ID's per frame
sns.lineplot(data=unique_ids, ax=ax, color='red')
plt.xlabel('Time (m)')
plt.ylabel('Birds')
# Set title to input_file
plt.title('Birds next to seeds over time in ' + imput_file)
# set ticks to 0 to total_length_sec
# Set ylim to 12
plt.ylim(0, 12)
# Set xlim to 0 to total_length_sec
plt.xlim(0, last_minute)
# tight layout
plt.tight_layout()
plt.savefig(imput_file + '_distance.png')