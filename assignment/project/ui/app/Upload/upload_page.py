import streamlit as st
import cv2
import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from ultralytics import YOLO
base_dir = "/app" 

def loadCSV():
    """
    Load CSV files in Pandas
    """
    
    print(base_dir)
    csv_path_train_csv = os.path.join(base_dir, "data", "csv", "annotations_train.csv")
    csv_path_test_csv  = os.path.join(base_dir, "data", "csv", "annotations_test.csv")
    csv_path_val_csv   = os.path.join(base_dir, "data", "csv", "annotations_val.csv")


    df_train = pd.read_csv(csv_path_train_csv , header=None)
    df_test  = pd.read_csv(csv_path_test_csv  , header=None)
    df_val   = pd.read_csv(csv_path_val_csv   , header=None)

    return df_train,df_test,df_val


def show_image_with_bb(df, image_path):
    image = cv2.imread(image_path)
    if image is None:
        st.error(f"❌ No se pudo cargar la imagen {image_path}")
        return None

    for _, row in df[df[0] == os.path.basename(image_path)].iterrows():
        x_min, y_min, x_max, y_max = map(int, row[1:5])
        label = row[5]
        
        
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    return Image.fromarray(image_rgb)


model = YOLO("yolov8n.pt")  


def show_blank_space(image_path):
    """Detecta productos en la estantería y resalta los espacios vacíos."""

    
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ No se pudo cargar la imagen {image_path}")
        return None

    image_result = image.copy()

    
    results = model(image, conf=0.2)  

   
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    bounding_boxes = []
    print("📦 Detecciones encontradas:")
    for result in results:
        for box in result.boxes:
            x_min, y_min, x_max, y_max = map(int, box.xyxy[0])  
            label = result.names[int(box.cls[0])]  
            confidence = box.conf[0]  

            print(f"➡️ {label} detectado con {confidence:.2f} en ({x_min}, {y_min}), ({x_max}, {y_max})")

            bounding_boxes.append((x_min, y_min, x_max, y_max))
            cv2.rectangle(image_result, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  

            
            cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, thickness=cv2.FILLED)

    
    cv2.imwrite("debug_mask.jpg", mask)


    if np.count_nonzero(mask) == 0:
        print("⚠️ No se detectaron productos en la máscara. Creando máscara blanca.")
        mask_inv = np.ones(mask.shape, dtype=np.uint8) * 255  
    else:
        mask_inv = cv2.bitwise_not(mask)  

    
    cv2.imwrite("debug_mask_inv.jpg", mask_inv)

    
    contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("⚠️ No se encontraron espacios vacíos.")
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h > 500:  
            print(f"🔴 Espacio vacío detectado en ({x}, {y}), tamaño: {w}x{h}")
            cv2.rectangle(image_result, (x, y), (x + w, y + h), (0, 0, 255), 3)  

    
    image_result = cv2.cvtColor(image_result, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_result)


def show_image_upload():
    st.markdown("<h1 style='text-align: center;'>📷 Subir Imagen</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📤 Selecciona una imagen...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        
        image_path = f"{uploaded_file.name}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.read())

        df_train,df_test,df_val = loadCSV()

       
        processed_image = show_image_with_bb(df_val, image_path)
        
        processed_image_b = show_blank_space(image_path)

        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📌 Imagen Original")
            st.image(image_path, use_container_width=True)

        with col2:
            if processed_image is not None:
                st.markdown("### ✏️ Imagen con Bounding Boxes")
                st.image(processed_image, caption="Imagen con Bounding Boxes", use_container_width=True)

        with col3:
            if processed_image_b is not None:
                st.markdown("### ✏️ Imagen con  BB en Blanco")
                st.image(processed_image_b, caption="Imagen con BB en Blanco", use_container_width=True)

    if st.button("🔴 Cerrar Sesión"):
        st.session_state.clear() 
        st.rerun()  

