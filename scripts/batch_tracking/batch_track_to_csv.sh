# This script is used to batch process videos with the YOLOv8 and save the results to a project directory,
# as well as convert the raw avi file into to resized and compressed mp4 format.
# Requirements: Python 3.9 (tested), ffmpeg, YOLO model file and all dependencies.

VID_PATH=/path/to/videos*/*.mp4

export YOLO_MODEL_PATH=model_birds/birds.pt
export IMGSZ=2304
export SAVE_PROJECT_PATH=/save/path/project_name

# Ask the user if they want to continue if the project directory already exists
if [ -d "$SAVE_PROJECT_PATH" ]; then
    echo -e "Project directory already exists, files can be overwritten. Content:\n\n$SAVE_PROJECT_PATH\n"
    ls -la $SAVE_PROJECT_PATH
    echo -e "\n\nPath that will be processed:\n\n$VID_PATH\n\nDo you want to continue? (y/n)"
   
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Exiting"
        exit 1
    fi
fi

# Create a project directory if it doesn't exist
if [ ! -d "$SAVE_PROJECT_PATH" ]; then
    mkdir -pv $SAVE_PROJECT_PATH
fi

for i in $VID_PATH
    do
        export INPUT_VIDEO_PATH=$i
        echo $INPUT_VIDEO_PATH
        # Get the name of the file
        INPUT_FNAME=$(basename $i)
        echo "Input file name: $INPUT_FNAME"
        RAW_AVI_PATH=$SAVE_PROJECT_PATH/$INPUT_FNAME/$(basename $i .mp4).avi
        printf "Raw avi path: $RAW_AVI_PATH\n"
        python track_to_csv.py
        echo "Done with $i, converting to mp4" &
        # Compress and scale down the raw avi file to mp4 for future reference
        ffmpeg -y -i $RAW_AVI_PATH -c:v h264_nvenc -filter:v scale=1280:-1 -cq 45 $SAVE_PROJECT_PATH/$(basename $i .mp4)_detections.mp4
        rm $RAW_AVI_PATH # Remove the huge avi file
    done

echo "Done tracking all videos. When the ffmpeg process is done, avi files will be safe to delete."
# Check if ffmpeg is done
wait
echo "All done"
