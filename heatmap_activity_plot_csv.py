import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import sys
import gc
import os
import numpy as np

imput_path = sys.argv[1]
input_date = sys.argv[2]

if not input_date:
    input_date = '0803'

# Load all csv files in the input path
files = []
for file in os.listdir(imput_path):
    # File should start with 'feeding_count' and end with '.csv' and contrains '_07' in the middle
    if file.startswith('feeding_count') and file.endswith('.csv') and '000' and input_date in file:
        files.append(file)


# sort the files
files.sort()
print(files)

# Concatinate all the files, only keep one 't' column
df = pd.concat([pd.read_csv(imput_path + file, usecols=[0,1]) for file in files], axis=0, ignore_index=True)
# Remove duplicate 't' column
df = df.loc[:,~df.columns.duplicated()]
# Convert t column to index
df.set_index('t', inplace=True)
print(df)
# Store column name as expdate
expdate = df.columns[0]
print(expdate)
# Transpose the dataframe
df = df.T
# Create a heatmap plot
fig, ax = plt.subplots(figsize=(20, 1))


# # Adjust the cmap to values from 0 to 12
# my_cmap = sns.diverging_palette(220, 20, n=12)
# sns.heatmap(df, cmap=my_cmap, vmin=0, vmax=12, ax=ax)
sns.heatmap(df, cmap='coolwarm', ax=ax)
# Draw vertical lines to separate hours
for i in range(0, 12):
    ax.axvline(x=i*10, color='black', linewidth=5, ymin=0.3, ymax=0.7, marker='*')
    # add marker to the line
    #ax.text(i*10, 0, int(i)+7, fontsize=20, color='black', ha='center', va='bottom')
# Adjust the cmap to values from 0 to 12

# Hide colorbar
ax.collections[0].colorbar.remove()
# Remove ticks
ax.set_xticks([])
# Set x labels to 7 to 18 with step 1
# ax.set_xticks(np.arange(0, len(df.columns), 100))
# ax.set_xticklabels(df.columns[ax.get_xticks()], fontsize=20)
# Rotate y labels to horizontal
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=20)
# Hide x title
ax.set_xlabel('')
#tight layout
plt.tight_layout()
#plt.show()
plt.savefig(imput_path + expdate + '_feeding_heatmap.png')