import time
import boto3
import psycopg2
from datetime import datetime
from PIL import Image as Img
from app import settings as config
from sqlalchemy import create_engine,and_
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy import insert
from sqlalchemy import func
from app.image.models import Image, DetectedProduct, MissingProduct, ImageProcessingLog
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse
from io import BytesIO
import base64
LOGGER = logging.getLogger(__name__)
s3_client = boto3.client(
    's3',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID_OUTPUT,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY_OUTPUT,
    #aws_session_token=config.AWS_SESSION_TOKEN_OUTPUT
)


DATABASE_USERNAME = config.DATABASE_USERNAME
DATABASE_PASSWORD = config.DATABASE_PASSWORD
DATABASE_HOST = config.DATABASE_HOST
DATABASE_NAME = config.DATABASE_NAME


SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


Session = sessionmaker(bind=engine)
session = Session()

async def insert_image_record(file):

    try:
        
        LOGGER.warning("Cannot determine default source to look up family name.")
       
        current_date = datetime.now().strftime("%Y-%m-%d") 
        processed_image_name = f"processed_{int(time.time())}.jpg"

        s3_image_key = f"{config.S3_BUCKET_PREFIX_OUTPUT}{current_date}/{processed_image_name}"
        file_size = len(file.file.read())
        LOGGER.warning(file_size)
        file.file.seek(0)
        s3_client.upload_fileobj(file.file, config.S3_BUCKET_NAME_OUTPUT, s3_image_key)

        s3_url = f"https://{config.S3_BUCKET_NAME_OUTPUT}.s3.amazonaws.com/{s3_image_key}"

       
        insert_stmt = insert(Image).values(image_name=file.filename, s3_url=s3_url).returning(Image.image_id)


        result = session.execute(insert_stmt)

        image_id = result.fetchone()[0]


        session.commit()

        LOGGER.info(f"Image inserted with ID: {image_id}")

        return image_id
    
    except Exception as e:
        
        LOGGER.error(f"❌ rollback: {e}")
        session.rollback()
        
        if 'image_id' in locals():  
            new_log = ImageProcessingLog(image_id=image_id, log_message=str(e))
            session.add(new_log)
            session.commit()  
    finally:
        session.close()

def insert_detected_product(result_id, product_name):
    if not session:
        LOGGER.error("Invalid session to insert the detected product.")
        return None
  
    try:
        stmt = insert(DetectedProduct).values(
            image_id=result_id,
            product_name=product_name
        )
        session.execute(stmt)
        session.commit()
        LOGGER.info(f"Detected product inserted: {product_name}")
    except Exception as e:
        LOGGER.error(f"Error inserting product detected: {e}")
        raise

def insert_missing_product( result_id, product_name):
    if not session:
        LOGGER.error("Invalid session to insert the missing product.")
        return None
    
    try:
        stmt = insert(MissingProduct).values(
            image_id=result_id,
            product_name=product_name
        )
        session.execute(stmt)
        session.commit()
        LOGGER.info(f"Missing product inserted: {product_name}")
    except Exception as e:
        LOGGER.error(f"Error inserting missing product: {e}")
        raise

def number_of_images_processed():
    LOGGER.warning("Entering the number_of_images_processed")
    if not session:
        LOGGER.error("Invalid session to insert the missing product.")
        return None
    
    try:

        stmt = session.query(
            func.date(Image.created_at).label('date'), 
            func.count().label('amount')  
        ).group_by(func.date(Image.created_at)).order_by('date')

        
        data = stmt.all()  
        
        if not data:
            LOGGER.info("No processed images found by date.")
            return []


        processed_images = [{"date": row[0], "amount": row[1]} for row in data]
        return processed_images

    except Exception as e:
        LOGGER.error(f"Error executing query: {e}")
        return None
    
def number_of_products_detected(id_image):
    LOGGER.warning("Entering the number_of_products_detected")
    if not session:
        LOGGER.error("Invalid session to view products.")
        return None
    
    try:
  
        stmt = session.query(
            Image.image_name,  
            func.date(Image.created_at).label('date'),  
            func.count(func.distinct(DetectedProduct.product_id)).label('total_detected'),  
            func.count(func.distinct(MissingProduct.missing_id)).label('total_missing') 
        ).outerjoin(DetectedProduct, DetectedProduct.image_id == Image.image_id)  
        stmt = stmt.outerjoin(MissingProduct, MissingProduct.image_id == Image.image_id)  
        stmt = stmt.filter(Image.image_id == id_image)  
        stmt = stmt.group_by(func.date(Image.created_at), Image.image_id, Image.image_name)  
        stmt = stmt.order_by('date')  
        
        data = stmt.all()

        if not data:
            LOGGER.info(f"No products were found for the image with id {id}.")
            return []

  
        processed_images = [{"image_name": row[0], "date": row[1], "total_detected": row[2], "total_missing": row[3]} for row in data]
        LOGGER.warning(processed_images)
        return processed_images

    except Exception as e:
        LOGGER.error(f"Error executing query: {e}")
        return None
    
def total_of_products_detected(id_image):
    LOGGER.warning("Entering the total_of_products_detected")
    
    if not session:
        LOGGER.error("Invalid session to view products.")
        return None
    
    try:
        
        stmt = session.query(
            DetectedProduct.product_name,
            func.count(func.distinct(DetectedProduct.product_id)).label('total_detected')  
        ).filter(DetectedProduct.image_id == id_image) 
        stmt = stmt.group_by(DetectedProduct.product_name)  
        stmt = stmt.order_by(func.count(func.distinct(DetectedProduct.product_id)).desc())
        
        data = stmt.all()

        if not data:
            LOGGER.info(f"No products were detected for the image with id {id_image}.")
            return []

     
        detected_products = [{"product_name": row[0], "total_detected": row[1]} for row in data]
        return detected_products

    except Exception as e:
        LOGGER.error(f"Error executing query: {e}")
        return None
    
def get_image_detection_report(image_id):
    LOGGER.info(f"Getting detection report for image with ID: {image_id}")

    if not session:
        LOGGER.error("Invalid session to view the report.")
        return None

    try:
        image = session.query(Image).options(
            joinedload(Image.detected_products),
            joinedload(Image.missing_products)
        ).filter(Image.image_id == image_id).first()

        if not image:
            LOGGER.info(f"No information found for image with ID {image_id}.")
            return None

        detected_count = len(image.detected_products)
        missing_count = len(image.missing_products)

        detection_rate = "100%" if missing_count == 0 else f"{round((detected_count * 100) / (detected_count + missing_count), 2)}%"
        
        image.created_at = image.created_at.strftime("%Y-%m-%d")
        
        report = {
            "image_id": image.image_id,
            "image_name": image.image_name,
            "s3_url": image.s3_url,
            "created_at": image.created_at,
            "detected_products": detected_count,
            "missing_products": missing_count,
            "detection_rate": detection_rate,
            "detected_product_list": [{"product_name": p.product_name} for p in image.detected_products],
            "missing_product_list": [{"product_name": p.product_name} for p in image.missing_products]
        }

        return report

    except Exception as e:
        LOGGER.error(f"Error on get_image_detection_report: {e}")
        return None
    

def get_image_detection_all(start_date, end_date):
    LOGGER.warning("Entering the fetchGrid")

    if not session:
        LOGGER.error("Invalid session to view images.")
        return []

    try:
        # Convertir las fechas al formato correcto

        LOGGER.warning(f"Start Date: {start_date}")
        LOGGER.warning(f"End Date: {end_date}")

        stmt = session.query(
            Image.image_id.label("N-REGISTER"),
            Image.image_name.label("NAME"),
            Image.created_at.label("DATE")
        ).filter(
            func.date(Image.created_at).between(start_date, end_date)
        ).order_by(Image.created_at.desc())

        data = stmt.all()

        if not data:
            LOGGER.info(f"No images found in the date range {start_date} - {end_date}.")
            return []

        processed_images = [{"N-REGISTER": row[0], "NAME": row[1], "DATE": row[2]} for row in data]
        LOGGER.warning(f"processed_images: {processed_images}")
        return processed_images

    except Exception as e:
        LOGGER.error(f"Error executing query: {e}")
        return []
    
    
def image_s3(s3_url):

    bucket_name, object_key = get_object_key_from_url(s3_url)
    LOGGER.error(f"bucket_name: {bucket_name}")
    LOGGER.error(f"object_key: {object_key}")
    # Descargar la imagen desde S3
    img_data = download_image_from_s3(bucket_name, object_key)
    
    if not img_data:
        LOGGER.error(f"Could not get image from S3: {img_data}")
    img = Img.open(BytesIO(img_data))

       
    buffered = BytesIO()
    img.save(buffered, format="PNG")  # Guarda la imagen en formato PNG o el que desees
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return img_base64
    
def get_object_key_from_url(s3_url):
    # Parsear la URL de S3 para obtener el bucket y la clave
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc.split('.')[0]  # Obtener el nombre del bucket
    object_key = parsed_url.path.lstrip('/')  # Obtener la clave del objeto
    return bucket_name, object_key

def download_image_from_s3(bucket_name, object_key):
    # Descargar el archivo de S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    img_data = response['Body'].read()  # Leer el archivo binario
    return img_data
