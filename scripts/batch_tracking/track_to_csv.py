# This python script is called by bash script called batch_track_to_csv.sh
#
# To run directly, assign the bash environment variables:
# export INPUT_VIDEO_PATH=example.mp4 IMGSZ=800 YOLO_MODEL_PATH=models/8small1280.pt
# export SAVE_PROJECT_PATH=project_name/
# python track_csv.py

import csv
from ultralytics import YOLO
import os

input_video = os.getenv("INPUT_VIDEO_PATH")
save_path = os.getenv("SAVE_PROJECT_PATH")
yolo_model = os.getenv("YOLO_MODEL_PATH")
imgsz = int(os.getenv("IMGSZ"))
video_name = os.path.basename(input_video)
csv_fname = save_path + '/' + video_name + '.csv'

# Load an official or custom model
model = YOLO(yolo_model)

# Read classes.txt file to get the class names
classes = []
with open("classes.txt", "r") as file:
    classes = file.read().split("\n")
# Remove empty strings
classes = list(filter(None, classes))
print(classes)
print(f"Processing video: {input_video}")

# Setting up CSV to save the data
with open(csv_fname, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["frame", "class", "ID", "conf", "X1", "Y1", "X2", "Y2", "center_x", "center_y"])
    print(f"CSV file created: {csv_fname}")

    # Process video and track frame by frame
    for frame_idx, result in enumerate(model.track(source=input_video,imgsz=imgsz,stream=True, save_json=True,
                                                   show=False,save=True,line_width=3, tracker="model_birds/birds.yaml",
                                                   project=save_path, name=video_name, exist_ok=True)):
        for det in result.boxes.data.tolist():  # Adjust this line based on the actual structure of the result
            x1, y1, x2, y2, track_id, conf, cls = det  # Corrected order
            #print(f"Detection: x1={x1}, y1={y1}, x2={x2}, y2={y2}, cls={cls}, conf={conf}, track_id={track_id}")
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            # Calculate the center of the bounding box
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            class_name = classes[int(cls)]
            # Round confidence to 2 decimal places
            conf = round(conf, 2)
            writer.writerow([frame_idx, class_name, int(track_id), conf, x1, y1, x2, y2, center_x, center_y])
