# Correct bad detections in the label files generated with YOLOv8 using labelImg.
# To do this, some columns need to be removed from the label files, otherwise
# labelImg will complain.

# This script iterates through each txt file in the folder, load as tsv and remove the last two columns.
# To remove one column, use df = df.iloc[:, :-1] on line 18.

import os
import pandas as pd
import sys

# Read path as first command line argument
path = sys.argv[1]

for file in os.listdir(path):
    if file.endswith('.txt'):
        # Load the file as a space separated file
        df = pd.read_csv(os.path.join(path, file), sep=' ')
        # print head
        print(df.head())
        # Remove the last two columns
        df = df.iloc[:, :-2]
        # print head
        print(df.head())
        # rename the original file
        os.rename(os.path.join(path, file), os.path.join(path, file.replace('.txt', '_original.txt')))
        # Save the new file
        df.to_csv(os.path.join(path, file), sep=' ', index=False)
        