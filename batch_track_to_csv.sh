# This script is used to batch process videos with the YOLO tracker and save the results to a project directory,
# as well as convert the raw avi file into to resized and compressed mp4 format.
# Requirements: Python 3.9 (test), ffmpeg, YOLO model file and all dependencies.

VID_PATH=~/Videos/file*.mp4
export YOLO_MODEL_PATH=models/8small1280.pt
export IMGSZ=600
export SAVE_PROJECT_PATH=~/Videos/tracked/8small1280

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
        python track_csv.py
        echo "Done with $i, converting to mp4" &
        ffmpeg -y -i $RAW_AVI_PATH -c:v h264_nvenc -filter:v scale=1280:-1 -cq 45 $SAVE_PROJECT_PATH/$(basename $i .mp4)_detections.mp4 &  
    done

echo "Done tracking all videos. When the ffmpeg process is done, avi files will be safe to delete."
# Check if ffmpeg is done
wait
echo "All done"
