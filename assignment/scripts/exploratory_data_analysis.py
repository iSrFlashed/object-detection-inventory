import pandas as pd
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
import random
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def loadCSV():
    """
    Load CSV files in Pandas
    """
    
    print(base_dir)  
    csv_path_train_csv = os.path.join(base_dir, "data", "csv", "annotations_train.csv")
    csv_path_test_csv  = os.path.join(base_dir, "data", "csv", "annotations_test.csv")
    csv_path_val_csv   = os.path.join(base_dir, "data", "csv", "annotations_val.csv")
    csv_path_train_img = os.path.join(base_dir, "data", "images", "train")
    csv_path_test_img  = os.path.join(base_dir, "data", "images", "test")
    csv_path_val_img   = os.path.join(base_dir, "data", "images", "val")

  
    df_train = pd.read_csv(csv_path_train_csv , header=None)
    df_test  = pd.read_csv(csv_path_test_csv  , header=None)
    df_val   = pd.read_csv(csv_path_val_csv   , header=None)

    
    print("\n" + "="*50)
    print("📊 Resumen de datos (Train)")
    print("="*50)
    print(df_train.head(), "\n")
    print(df_train.info(), "\n")
    print(df_train.describe(), "\n")

    
    print("\n" + "="*50)
    print("📊 Resumen de datos (Test)")
    print("="*50)
    print(df_test.head(), "\n")
    print(df_test.info(), "\n")
    print(df_test.describe(), "\n")

   
    print("\n" + "="*50)
    print("📊 Resumen de datos (Val)")
    print("="*50)
    print(df_val.head(), "\n")
    print(df_val.info(), "\n")
    print(df_val.describe(), "\n")

    
    train_images = len(os.listdir(csv_path_train_img))
    test_images = len(os.listdir(csv_path_test_img))
    val_images = len(os.listdir(csv_path_val_img))

    
    print("\n" + "="*50)
    print("📊 Estadísticas de imágenes y anotaciones")
    print("="*50)
    print(f"📌 Train: {train_images} imágenes, {len(df_train)} anotaciones")
    print(f"📌 Test: {test_images} imágenes, {len(df_test)} anotaciones")
    print(f"📌 Val: {val_images} imágenes, {len(df_val)} anotaciones")
    print("="*50 + "\n")

    return df_train,df_test,df_val

def is_image_corrupt(img_path):
 
    try:
        
        with Image.open(img_path) as img:
            img.verify()
        
        
        with Image.open(img_path) as img:
            img_array = np.array(img.convert("RGB"))
        
        
        height, width, _ = img_array.shape
        if height < 10 or width < 10:
            print(f"⚠️ Imagen muy pequeña, posible corrupción: {img_path}")
            return True
        
        
        mid_x = width // 2  
        front_part = img_array[:, :mid_x, :]  
        back_part = img_array[:, mid_x:, :]   
        
      
        if not np.all(front_part == 0):
            print(f"⚠️ Imagen con datos en la parte delantera, posible corrupción: {img_path}")
            plt.figure(figsize=(4, 4))
            plt.imshow(front_part)
            plt.axis("off")  
            plt.title("Parte Delantera - Posible Corrupción")
            plt.show()
            
            return True
        
        print("✅ Imagen válida (parte frontal está negra, parte trasera es la buena).")
        return False
    
    except Exception as e:
        print(f"❌ Error al procesar la imagen, posible corrupción: {img_path} ({e})")
        return True


def clean_csv(df, image_folder):
    
    df_cleaned = df[df[0].apply(lambda img: os.path.exists(os.path.join(base_dir,image_folder, img)))]
   
    corrupted_images = []
   
    valid_images = []
    
    for img_name in df_cleaned[0]:
        img_path = os.path.join(base_dir, image_folder, img_name)
        if is_image_corrupt(img_path):
            corrupted_images.append({'image_name': img_name, 'image_path': img_path, 'error': 'Imagen Dañada'})
        else:
            valid_images.append(img_name)
        

    with open(os.path.join(base_dir, 'data', 'csv', 'corrupted_images.txt'), 'w') as f:
        for entry in corrupted_images:
            f.write(f"Name: {entry['image_name']}, Ruta: {entry['image_path']}, Error: {entry['error']}\n")

    df_cleaned = df_cleaned[df_cleaned[0].isin(valid_images)]
    
  
    df_cleaned = df_cleaned[(df_cleaned[1] < df_cleaned[3]) & (df_cleaned[2] < df_cleaned[4])]

    return df_cleaned

def show_image_with_bb(df, image_folder):
    
    img_name = random.choice(df[0].unique())
    img_path = os.path.join(image_folder, img_name)

    
    image = cv2.imread(img_path)
    if image is None:
        print(f"❌ No se pudo cargar la imagen {img_name}")
        return

    
    for _, row in df[df[0] == img_name].iterrows():
        x_min, y_min, x_max, y_max = row[1:5]
        label = row[5]
        
       
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    
    plt.figure(figsize=(8, 8))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()





def process_image_annotations(img_name, group, labels_folder, class_dict):
    
    label_path = Path(labels_folder) / img_name.replace(".jpg", ".txt")

    with open(label_path, "w") as f:
        for _, row in group.iterrows():
            class_id = class_dict.get(row["class"], -1)
            if class_id == -1:
                print(f"⚠️ Clase desconocida: {row['class']} en {img_name}")
                continue

            x_min, y_min, x_max, y_max = row["x_min"], row["y_min"], row["x_max"], row["y_max"]
            img_width, img_height = row["img_width"], row["img_height"]

        
            x_center = ((x_min + x_max) / 2) / img_width
            y_center = ((y_min + y_max) / 2) / img_height
            width = (x_max - x_min) / img_width
            height = (y_max - y_min) / img_height

            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def convert_csv_to_yolo(csv_file, labels_folder, num_threads=4):
    
    df = pd.read_csv(csv_file, header=None, names=["image", "x_min", "y_min", "x_max", "y_max", "class", "img_width", "img_height"])
    os.makedirs(labels_folder, exist_ok=True)

    class_dict = {"object": 0, "empty_space": 1}  

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for img_name, group in df.groupby("image"):
            futures.append(executor.submit(process_image_annotations, img_name, group, labels_folder, class_dict))

        for future in futures:
            future.result()  

    print(f"✅ CSV convertido y guardado en {labels_folder}")


def check_labels(image_folder, label_folder):
    
    image_files = {f.replace(".jpg", "") for f in os.listdir(image_folder) if f.endswith(".jpg")}
    label_files = {f.replace(".txt", "") for f in os.listdir(label_folder) if f.endswith(".txt")}

    missing_labels = image_files - label_files
    missing_images = label_files - image_files

    if missing_labels:
        print(f"⚠️ Faltan {len(missing_labels)} etiquetas en {label_folder}:")
        for name in missing_labels:
            print(f"   - {name}.jpg no tiene {name}.txt")

    if missing_images:
        print(f"⚠️ {len(missing_images)} etiquetas en {label_folder} no tienen imagen en {image_folder}:")
        for name in missing_images:
            print(f"   - {name}.txt no tiene {name}.jpg")

    if not missing_labels and not missing_images:
        print(f"✅ Todas las imágenes en {image_folder} tienen su etiqueta en {label_folder}")
