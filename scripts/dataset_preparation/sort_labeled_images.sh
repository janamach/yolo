# This script goes through a folder and looks for filenames that exist in *txt and *jpg format.
# It then moves these files to "labels" and "images" folders respectively, while ignoring
# images that do not have a corresponding label file.
# This is usful when generating a clean dataset for training a YOLO model.

new_dir_name="combined_dataset"
new_train_dir_name="combined_dataset/train"
new_val_dir_name="combined_dataset/validate"

# Check if the user has provided a folder name
if [ -z "$1" ]; then
    echo "Please provide a folder name."
    exit 1
fi

# Check if the folder exists
if [ ! -d "$1" ]; then
    echo "Folder does not exist."
    exit 1
fi

# Check if the folder is empty
if [ ! "$(ls -A $1)" ]; then
    echo "Folder is empty."
    exit 1
fi

# Create "labels" and "images" folders
mkdir -p ${new_train_dir_name}/labels
mkdir -p ${new_train_dir_name}/images

# Check if the file exists in the new folder
if [ -f "${new_train_dir_name}/labels/classes.txt" ]; then
# Compare the contents of the files
    if cmp "$1/classes.txt" ${new_train_dir_name}/labels/classes.txt; then
    info_classes="classes.txt file already exists in the new folder and they are the same.\n"
    else
        echo -e "\nclasses.txt file exists in the new folder but the contents are different."
        echo -e "\nRunning diff command...\n"
        diff "$1/classes.txt" ${new_train_dir_name}/labels/classes.txt
        echo -e "\nExiting...\n"
        exit 1
    fi
else 
    cp -v $1/classes.txt ${new_train_dir_name}/labels/
    info_classes="classes.txt file does not exist in the new folder, so it has been copied.\n"
fi

# Move files to "labels" and "images" folders
for file in $1/*; do
    # If all the other files that are not classes.txt are in jpg and txt format, copy them to the new folder:
    if [ -f "$file" ] && [[ "$file" != *classes.txt ]]; then
        filename=$(basename -- "$file")
        extension="${filename##*.}"
        filename="${filename%.*}"
        if [ -f "$1/$filename.txt" ]; then
            cp -v $1/$filename.txt ${new_train_dir_name}/labels
            cp -v $1/$filename.jpg ${new_train_dir_name}/images
        fi
    fi
done

# Check if one of the files in the new folder is contains "reference" in its name and ask user if they want to delete it
if ls ${new_train_dir_name}/labels/*reference* 1> /dev/null 2>&1; then
    echo -e "One of the files in the labels folder contains 'reference' in its name."
    # Print out the file names
    echo -e "\nFiles containing 'reference' in their names:"
    ls ${new_train_dir_name}/labels/*reference*
    ls ${new_train_dir_name}/images/*reference*
    read -p "Do you want to delete it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -v ${new_train_dir_name}/labels/*reference*
        rm -v ${new_train_dir_name}/images/*reference*
    fi
fi

# Print out the number of files in the new folders
no_of_labels=$(ls -1 ${new_train_dir_name}/labels | wc -l)
echo -e "\nNumber of files in labels folder: ${no_of_labels}"
echo -e "Number of files in images folder: $(ls -1 ${new_train_dir_name}/images | wc -l)\n"
echo -e $info_classes

# Ask user if they want to split the dataset into training and validation sets
read -p "Do you want to split the dataset into training and validation sets? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "The total number of labels in the new folder is ${no_of_labels}, taking 20% of it as validation set."
    no_of_validation=$(echo "$no_of_labels * 0.2" | bc | awk '{print int($1)}')

    # Create "validate" folder
    mkdir -p ${new_val_dir_name}/labels
    mkdir -p ${new_val_dir_name}/images

    # Move random files to "validate" folder
    for file in $(ls ${new_train_dir_name}/labels | shuf -n ${no_of_validation}); do
        filename="${file%.*}"
        #if filename is not classes.txt
        if [[ "$filename" != *classes* ]]; then
            mv -v ${new_train_dir_name}/labels/${filename}.txt ${new_val_dir_name}/labels/
            mv -v ${new_train_dir_name}/images/${filename}.jpg ${new_val_dir_name}/images/
        fi
    done
    cp -v ${new_train_dir_name}/labels/classes.txt ${new_val_dir_name}/labels/
fi