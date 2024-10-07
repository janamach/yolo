import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import sys
import gc
import os
import numpy as np

fps=30

imput_file = sys.argv[1]

# extract date from the input file:
group = 'Group ' + imput_file.split('/B')[-1].split('_')[0]
groupb = imput_file.split('/')[-1].split('_')[0]

date = imput_file.split('_')[1]
time = imput_file.split('_')[2].split('.')[0]
# create time string with HH:MM
time_HHMM = time[:2] + ':' + time[2:-2]
time_HHM = time[:2] + time[2:]
# Create date string with M DD
month = date[4:6]
if month == '07':
    month = 'Jul'
else:
    month = 'Aug'
date_mmdd = month + ' ' + date[6:]
basename = imput_file.split('/')[-1].split('.')[0]
identifier = date + '_' + time + '_' + groupb
identifierd = date + '_' + groupb

title = group + "  ***  " + date_mmdd + ' at ' + time_HHMM

# Get path of the input file:
path = '/'.join(imput_file.split('/')[:-1])
output_path = path + '/output'

print(path, group, date, time, basename)

# Create output folder if it does not exist
if not os.path.exists(output_path):
    os.makedirs(output_path)
if not os.path.exists(output_path + '/ref'):
    os.makedirs(output_path + '/ref')

# Read the CSV file
df = pd.read_csv(imput_file)

# Calculate total length of the video by subtracting the first frame from the last frame
# and dividing by the fps
first_frame = df['frame'].iloc[0]
last_frame = df['frame'].iloc[-1]
frames_total = (df['frame'].iloc[-1] - df['frame'].iloc[0]) / fps
print(frames_total)

# print head of the dataframe
print(df.head())

# The data in X1, Y1, X2, Y2, are for the bounding box. We can calculate the width and height of the bounding box
df['width'] = df['X2'] - df['X1']
df['height'] = df['Y2'] - df['Y1']

# make a separate df with two classes 'bird' and 'white' called df2
bdf = df[(df['class'] == 'bird') | (df['class'] == 'white')]
df = df[(df['class'] != 'bird') & (df['class'] != 'white')]

# In bf calculate the aea of the bounding box
bdf['area'] = bdf['width'] * bdf['height']

# Remove X1, Y1, X2, Y2 columns and reset index
#bdf = bdf.drop(columns=['X1', 'Y1', 'X2', 'Y2']).reset_index(drop=True)
dbf = bdf.reset_index(drop=True)

# Store median values ov classes in df
for class_name, cdf in df.groupby('class'):
    # pass is len(cdf) < 10000 to filter out false detections
    if len(cdf) < 15000:
        print(class_name, len(cdf))
        continue
    new_ID = cdf['ID'] == 0
    median_x1 = cdf['X1'].median()
    median_y1 = cdf['Y1'].median()
    meduan_x2 = cdf['X2'].median()
    median_y2 = cdf['Y2'].median()
    width = cdf['width'].median()
    height = cdf['height'].median()
    
    median_y = cdf['center_y'].median()
    median_x = cdf['center_x'].median()

    median_area = width * height

    # Concatinate the new values to bdf:
    bdf = pd.concat([bdf, pd.DataFrame({'frame': cdf['frame'].iloc[0], 'class': class_name, 'ID': 0, 'conf': 1,
                                        'X1': median_x1, 'Y1': median_y1, 'X2': meduan_x2, 'Y2': median_y2,
                                          'width': width, 'height': height, 'center_x': median_x, 'center_y': median_y,
                                        'area': median_area}, index=[0])], ignore_index=True)
    
# Dele the original df and do garbage collection to save memory
del df
gc.collect()

# print head of the dataframe
print(bdf.head())
print(bdf.tail(10))

# Save the objects_df and bdf to a csv file
bdf.to_csv(output_path + '/birds_' + basename + '.csv', index=False)

# Separate 'ID' == 0 inro objects_df
objects_df = bdf[bdf['ID'] == 0]
birds_df = bdf[bdf['ID'] != 0]

# Create ax and figure with fixes size
fig, ax = plt.subplots(figsize=(6, 4))

# plot the x_center, y_center of birds_df as a 2d histogram
hb = ax.hexbin(birds_df['X1'], birds_df['Y1'], gridsize=80, cmap='inferno', bins='log', extent=(0, 2304, 0, 1296))
#ax = sns.histplot(birds_df, x='X1', y='Y1', bins=20, cmap='inferno', cbar=True, cbar_kws={'label': 'log10(count)'})
# Set background color to the lowest value of the hexbin
ax.set_facecolor(plt.cm.inferno(0))


# plot the rectangles with width and height at x_center, y_center position
for class_name, cdf in objects_df.groupby('class'):
    for i, row in cdf.iterrows():
        ax.add_patch(plt.Rectangle((row['X1'], row['Y1']), row['width'], row['height'], fill=None, edgecolor='green', lw=4))
        # Add class_name to the rectangles
        ax.text(row['X1'], row['Y1'], class_name, color='cyan', fontsize=16)

# Set title to group, date and time
plt.title(title, fontsize=20)

# plot dimentions 2304x1296
plt.xlim(0, 2304)
plt.ylim(0, 1296)
# Hide ticks
plt.xticks([])
plt.yticks([])
plt.gca().invert_yaxis()
#plt.show()
# Tight layout
plt.tight_layout()

plt.savefig(output_path + '/heatmap_' + identifier + '.png')
plt.close()

total_distance = 0
# For birds_df, calculate distance traveled by each ID:
for bird_id, idf in birds_df.groupby('ID'):
    # Calculate the distance between the x_center and y_center of each frame
    # and store it in a new column called 'distance'
    idf['distance'] = ((idf['center_x'].diff()) ** 2 + (idf['center_y'].diff()) ** 2) ** 0.5
    # Calculate the total distance traveled by each ID
    distance = idf['distance'].sum()
    # Print the total distance traveled by each ID
    #print(bird_id, distance)
    total_distance += distance

# Print the average distance traveled by all birds
average_distance = total_distance / 12
# round the average distance to 2 decimal places
average_distance = round(average_distance, 2)

# Check if class "seeds" is in the objects_df
if 'seed_tank' in objects_df['class'].values:
    food = 'seed_tank'
elif 'seeds' in objects_df['class'].values:
    food = 'seeds'
else:
    food = None
print(food, identifier)
# Set ROI to the bounding box of food to countr birds feeding:
if food:
    food_df = objects_df[objects_df['class'] == food]
    x1_food = food_df['X1'].iloc[0]
    x2_food = food_df['X2'].iloc[0]
    y1_food = food_df['Y1'].iloc[0]
    y2_food = food_df['Y2'].iloc[0]
    print(x1_food, x2_food, y1_food, y2_food)
    # Create an empty df called feeding_df:
    feeding_df = pd.DataFrame()
    # Slice the birds_df to only include birds inside the food ROI
    feeding_df = birds_df[(birds_df['X2'] > x1_food) & (birds_df['X1'] < x2_food) &
                            (birds_df['Y2'] > y1_food) & (birds_df['Y1'] < y2_food)]
    # plot a heat map of the feeding birds
    fig, ax = plt.subplots(figsize=(6, 4))
    hb = ax.hexbin(feeding_df['X1'], feeding_df['Y1'], gridsize=80, cmap='inferno', bins='log')
    ax.set_facecolor(plt.cm.inferno(0))
    plt.xlim(0, 2304)
    plt.ylim(0, 1296)
    plt.gca().invert_yaxis()
    plt.savefig(output_path + '/ref/feeding_heatmap_' + identifier + '.png')
    plt.close()
    # Count the average number of ID's for each frame
    feeding_df = feeding_df.groupby('frame')['ID'].nunique()
    # Fill the missing frames with 0
    feeding_df = feeding_df.reindex(range(first_frame, last_frame + 1), fill_value=0)
    feeding_mean = feeding_df.mean()
    # Round mean to 2 decimal places
    feeding_mean = round(feeding_mean, 2)
    feeding_median = feeding_df.median()
    feeding_max = feeding_df.max()
    print(feeding_mean, feeding_median, feeding_max)
    # Save the info to a csv file with columns group, date, time, feeding_mean, feeding_median, feeding_max
    newdf = pd.DataFrame({ 'basename': [basename], 'group': [group], 'date': [date_mmdd], 'time': [time_HHMM], 'feeding_mean': [feeding_mean],
                            'feeding_median': [feeding_median], 'feeding_max': [feeding_max], 'average_movement': [average_distance]})
    # Save the header to a csv file
    header = pd.DataFrame({ 'basename': ['basename'], 'group': ['group'], 'date': ['date'], 'time': ['time'], 'feeding_mean': ['feeding_mean'],
                            'feeding_median': ['feeding_median'], 'feeding_max': ['feeding_max'], 'average_movement': ['average_movement']})
    header.to_csv(output_path + '/headers_feeding_' + groupb +'.csv', index=False, header=False)
    newdf.to_csv(output_path + '/feeding_' + basename + '.csv', index=False, header=False)

    # In feeding_df, get an average of the unique feeding birds per 30 frames
    # For each 30 frames, calculate the average of the unique ID's
    #feeding_df = feeding_df.rolling(window=30).median()
    # Move every 30th frame to a new df called feeding_df2, only include the last column and reset index
    feeding_df2 = feeding_df[::30*60].reset_index(drop=True)
    # Convert to pandas dataframe
    feeding_df2 = pd.DataFrame(feeding_df2)
    # Make index a column with the name 't'
    feeding_df2 = feeding_df2.reset_index()
    # Rename the columns to 't' and identifier
    feeding_df2.columns = ['t', identifierd]
    # add time_HHM to the 't' column
    feeding_df2['t'] = feeding_df2['t'] + int(time_HHM)
    #print(feeding_df2)
    # Save as csv file
    feeding_df2.to_csv(output_path + '/feeding_count_' + basename + '.csv', index=False, header=True)
else:
    # Create an empty df called feeding_df2 with only one column called 't'
    feeding_df2 = pd.DataFrame(columns=['t'])
    # Add time_HHM to the 't' column
    feeding_df2['t'] = range(1, 10)
    # Add time_HHM to the 't' column
    feeding_df2['t'] = feeding_df2['t'] + int(time_HHM)
    feeding_df2[identifierd] = 0
    #print(feeding_df2)
    feeding_df2.to_csv(output_path + '/feeding_count_' + basename + '.csv', index=False, header=True)

if 0:
    # Plot the feeding_df2 as a 1D heatmap with time on the x-axis and the number of feeding birds on the y-axis
    fig, ax = plt.subplots(figsize=(10, 1))
    # transpose the feeding_df2
    feeding_df2 = feeding_df2.T
    # remove the first row
    feeding_df2 = feeding_df2[1:]
    # print head
    print(feeding_df2.head())
    sns.heatmap(data=feeding_df2, ax=ax, cmap='inferno')
    # Set y label to identifier, rotate by 90 degrees
    plt.ylabel(date_mmdd + time_HHMM, rotation=0)
    #remove ticks
    plt.yticks([])
    plt.xticks([])
    # Hide cbar
    ax.collections[0].colorbar.remove()
    # Tight layout
    plt.tight_layout()
    # Move plot to the left side
    plt.subplots_adjust(left=0.4)
    plt.show()

quit()
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