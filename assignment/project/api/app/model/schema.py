from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class PredictRequest(BaseModel):
    file: str

class Response(BaseModel):
    success: bool
    id_image: Optional[int] = 0  
    detected_image:  Optional[str] = None
    detail: Optional[str] = None  
    status_code: Optional[int] = 200  

class ResponseDF(BaseModel):
    success: bool
    df: Optional[List[Dict[str, Union[str, int]]]] = None
    detail: Optional[str] = None 
    status_code: Optional[int] = 200  

class Product(BaseModel):
    product_name: str
    
class Report(BaseModel):
    image_id: int
    image_name: str
    s3_url: str
    created_at: str
    detected_products: int
    missing_products: int
    detection_rate: str
    detected_product_list: List[Product]
    missing_product_list: List[Product]

class ResponseReport(BaseModel):
    success: bool
    df: Report
    status_code: int
    detail: str