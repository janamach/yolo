# yolo

Download YOLO moveld from here: [YOLO Models](https://docs.ultralytics.com/models/)

## Bash commands:

Concatinate images horizontally:

    convert +append 1.jpg 2.jpg 3.jpg out.jpg

Concatinate images vertically:
    
    convert -append 1.jpg 2.jpg 3.jpg out.jpg

Run a python script in a bash for loop:

    for file in data/*.csv; do python3 script.py $file; done

Extract 1 frame per second from a video, and save 10 frames:
    
    input_video=1.mp4
    ffmpeg -i $input_video -vf fps=1 -frames:v 10 ${input_video}_%03d.jpg

Extract all frames from a video:

    ffmpeg -i 1s.mp4 %d.jpg


train:

    yolo train data=data.yaml model=models/yolov8m.pt epochs=1000 project="custom_models" name="8medium" batch=2


detect:

    model=models/yolov8s.pt
    source=1s.mp4
    output=../data/output/
    yolo detect $model $weights $source --save-txt --save-conf --save-crop --project $output


track:

    yolo track source='1s.mp4' model=models/yolov5mu.pt show=True conf=0.01 iou=0.5

export to tflite to use with Coral Edge TPU:

    yolo export model=models/yolov10s.pt format="edgetpu" imgsz=512

