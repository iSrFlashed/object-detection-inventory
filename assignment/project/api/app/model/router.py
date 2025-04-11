import os
from typing import List

from app import db
from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import  Response,ResponseDF,ResponseReport
from app.model.services import model_process,NumberImagesProcessedByDate,NumberProductsDetected,TotalProductsDetected,ImageDetectionReport,ImageS3,ImageDetectionAll
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
import json
from fastapi.responses import JSONResponse
import logging
LOGGER = logging.getLogger(__name__)
router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/process_image")
async def process_image(file: UploadFile, current_user=Depends(get_current_user)):
    rpse = {"success": False, "detected_image": None, "missing_image": None,"detail":None,"status_code":None}

    if not file or not utils.allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not supported.",
        )
    
    response  = await model_process(file)
  
    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    
    rpse["success"] = True
    rpse["id_image"]       = response_json.get("id_image")
    rpse["detected_image"] = response_json.get("detected_image")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")


    return Response(**rpse)

@router.get("/process_images_by_date")
async def process_images_by_date():
    rpse = {"success": False, "df": None,"detail":None,"status_code":None}
    

    response = await NumberImagesProcessedByDate() 

    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    rpse["success"] = True
    rpse["df"] =            response_json.get("df")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    return ResponseDF(**rpse)

@router.get("/detected_and_missing_products")
async def detected_and_missing_products(id_image: int):
    rpse = {"success": False, "df": None,"detail":None,"status_code":None}
    

    response = await NumberProductsDetected(id_image)  

    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    rpse["success"] = True
    rpse["df"] =            response_json.get("df")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    return ResponseDF(**rpse)

@router.get("/total_products_detected")
async def total_products_detected(id_image: int):
    rpse = {"success": False, "df": None,"detail":None,"status_code":None}
    

    response = await TotalProductsDetected(id_image)  

    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    rpse["success"] = True
    rpse["df"] =            response_json.get("df")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    return ResponseDF(**rpse)

@router.get("/image_detection_report")
async def image_detection_report(id_image: int):
    # Inicializamos la respuesta por defecto
    rpse = {"success": False, "df": None, "detail": None, "status_code": None}
    
 

    # Suponemos que ImageDetectionReport devuelve un JSONResponse o un diccionario
    response = await ImageDetectionReport(id_image)  # Aquí debes implementar esta función o importarla


    # Si la respuesta es un JSONResponse, accedemos al cuerpo y lo deserializamos
    if isinstance(response, JSONResponse):
        # Acceder al contenido del body y deserializarlo
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response
    
    # Creación del diccionario rpse con los datos que quieres retornar
    rpse = {
        "success": True,
        "df": response_json.get("df"),  # Puede que sea None si no existe
        "detail": response_json.get("detail", "No details provided"),  # Valor por defecto si falta
        "status_code": response_json.get("status_code", 200)  # Valor por defecto si falta
    }

    # Devuelve la respuesta final con la estructura de ResponseDF
    return ResponseReport(**rpse)



@router.get("/total_products_detected")
async def total_products_detected(id_image: int):
    rpse = {"success": False, "df": None,"detail":None,"status_code":None}
    

    response = await TotalProductsDetected(id_image)  

    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    rpse["success"] = True
    rpse["df"] =            response_json.get("df")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    return ResponseDF(**rpse)

@router.get("/image_detection_all")
async def image_detection_all(start_date: str, end_date: str):
    rpse = {"success": False, "df": None,"detail":None,"status_code":None}
    
    LOGGER.warning(f"Start Date: {start_date}")
    LOGGER.warning(f"End Date: {end_date}")
    response = await ImageDetectionAll(start_date, end_date) 

    if isinstance(response, JSONResponse):
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response  

    rpse["success"] = True
    rpse["df"] =            response_json.get("df")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    LOGGER.warning(f"Resultado del rpse image_detection_all: {rpse}")
    return ResponseDF(**rpse)

@router.get("/image_s3")
async def image_s3(s3_url: str):
    rpse = {"success": False, "detected_image": None,"detail":None,"status_code":None}


    LOGGER.warning("Antes de llamar a ImageS3")

    # Suponemos que ImageDetectionReport devuelve un JSONResponse o un diccionario
    response = await ImageS3(s3_url)  # Aquí debes implementar esta función o importarla
    LOGGER.warning(f"Resultado del response: {response}")

    # Si la respuesta es un JSONResponse, accedemos al cuerpo y lo deserializamos
    if isinstance(response, JSONResponse):
        # Acceder al contenido del body y deserializarlo
        response_json = json.loads(response.body.decode("utf-8"))
    else:
        response_json = response

    
    rpse["success"] = True
    rpse["id_image"]       = 0
    rpse["detected_image"] = response_json.get("detected_image")
    rpse["detail"]         = response_json.get("detail")
    rpse["status_code"]    = response_json.get("status_code")
    
    return Response(**rpse)