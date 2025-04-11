import os
import pandas as pd
import shutil
from pathlib import Path
import streamlit as st

UPLOAD_FOLDER = "dataset/images/train"
LABELS_FOLDER = "dataset/labels/train"

def save_uploaded_file(uploaded_file):
    """ Guarda el archivo en la carpeta UPLOAD_FOLDER """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def convert_csv_to_yolo(csv_file):
    """ Convierte annotations_train.csv al formato YOLO """
    df = pd.read_csv(csv_file, header=None, names=["image", "x_min", "y_min", "x_max", "y_max", "class", "img_width", "img_height"])
    os.makedirs(LABELS_FOLDER, exist_ok=True)
    
    class_dict = {"object": 0}  
    
    for _, row in df.iterrows():
        img_name = row["image"]
        x_min, y_min, x_max, y_max = row["x_min"], row["y_min"], row["x_max"], row["y_max"]
        img_width, img_height = row["img_width"], row["img_height"]
        class_id = class_dict[row["class"]]

        
        x_center = (x_min + x_max) / 2 / img_width
        y_center = (y_min + y_max) / 2 / img_height
        width = (x_max - x_min) / img_width
        height = (y_max - y_min) / img_height

        
        label_path = os.path.join(LABELS_FOLDER, img_name.replace('.jpg', '.txt'))
        with open(label_path, "a") as f:
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

    return f"CSV convertido y guardado en {LABELS_FOLDER}"
