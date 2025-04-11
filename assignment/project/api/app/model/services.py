from uuid import uuid4
import numpy as np
import torch
import cv2
import redis
from fastapi.responses import JSONResponse
import base64
from .. import settings
from ultralytics import YOLO
from app.process_image.image_detection_db import insert_image_record,insert_detected_product,insert_missing_product,number_of_images_processed,number_of_products_detected,total_of_products_detected,get_image_detection_report,image_s3,get_image_detection_all
import logging
LOGGER = logging.getLogger(__name__)

db = redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID)

model_path = "model/best.pt"
model = YOLO(model_path).to("cuda" if torch.cuda.is_available() else "cpu")


def img_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

async def model_process(file):
    print(f"Processing image {file}...")

    try:
     
        image_data = await file.read()
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(status_code=400, content={"detail": "Error al procesar la imagen"})

        class_colors = {
            0: (0, 255, 0),
            1: (0, 0, 255)
        }

        result_id =await  insert_image_record(file)

        results = model.predict(image, imgsz=640, conf=0.3)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordenadas de la caja
                class_id = int(box.cls[0])  # ID de la clase
                conf = box.conf[0]  # Confianza de la predicción

                color = class_colors.get(class_id, (255, 255, 255))

                # Dibujar la bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
                cv2.putText(image, f'{result.names[class_id]} {conf:.2f}',
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                product_name = result.names[class_id]
                if class_id == 0:
                    insert_detected_product(result_id, product_name)
                else :
                    insert_missing_product(result_id, product_name)

        detected_image = image.copy()

        detected_image_base64 = img_to_base64(detected_image)
        return JSONResponse(content={
            "id_image":result_id,
            "detected_image": detected_image_base64,
            "status_code":200,
            "detail":"sucess"
        })
    
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la imagen: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})



async def NumberImagesProcessedByDate():
    try:
        
       df = number_of_images_processed()
       if df is None:
            return JSONResponse(content={
                "status_code": 500,
                "detail": "Error al consultar la base de datos."
            })
       else:
            
            for image in df:
                image["date"] = image["date"].strftime("%Y-%m-%d")

       return JSONResponse(content={
            "df": df,
            "status_code":200,
            "detail":"sucess"
        })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    

async def NumberProductsDetected(id_image):
    try:
        
        df = number_of_products_detected(id_image)
       
        if df is None:
             
             return JSONResponse(content={
                 "status_code": 500,
                 "detail": "Error al consultar la base de datos."
             })
        else:
            
            for image in df:
                image["date"] = image["date"].strftime("%Y-%m-%d")

        return JSONResponse(content={
             "df": df,
             "status_code":200,
             "detail":"sucess"
         })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
async def TotalProductsDetected(id_image):
    try:
        
        df = total_of_products_detected(id_image)
       
        if df is None:
            
             return JSONResponse(content={
                 "status_code": 500,
                 "detail": "Error al consultar la base de datos."
             })

        return JSONResponse(content={
             "df": df,
             "status_code":200,
             "detail":"sucess"
         })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
async def ImageDetectionReport(id_image):
    try:
        
        df = get_image_detection_report(id_image)
        
        if df is None:
        
             return JSONResponse(content={
                 "status_code": 500,
                 "detail": "Error al consultar la base de datos."
             })

        return JSONResponse(content={
             "df": df,
             "status_code":200,
             "detail":"sucess"
         })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
async def ImageDetectionAll(start_date, end_dat):
    try:
        
        df = get_image_detection_all(start_date, end_dat)
       
        if df is None:
             
             return JSONResponse(content={
                 "status_code": 500,
                 "detail": "Error al consultar la base de datos."
             })
        else:
            
            for image in df:
                image["DATE"] = image["DATE"].strftime("%Y-%m-%d")

        return JSONResponse(content={
             "df": df,
             "status_code":200,
             "detail":"sucess"
         })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
async def ImageS3(s3_url):
    try:
        
        img = image_s3(s3_url)
        if img is None:
            return JSONResponse(content={
                "status_code": 500,
                "detail": "Error al consultar la base de datos."
            })


        return JSONResponse(content={
            "detected_image": img,
            "status_code":200,
            "detail":"sucess"
        })
    except Exception as e:
        LOGGER.error(f"Error en el procesamiento de la consulta: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})