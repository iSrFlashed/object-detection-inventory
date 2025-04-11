import requests
from PIL import Image
from app.settings import API_BASE_URL

def process_image(token: str, uploaded_file: Image) -> requests.Response:
    """This function calls the predict endpoint of the API to classify the uploaded
    image.

    Args:
        token (str): token to authenticate the user
        uploaded_file (Image): image to classify

    Returns:
        requests.Response: response from the API
    """
    
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
   
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE_URL}/model/process_image", headers=headers, files=files)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        error_response = requests.Response()
        error_response.status_code = 500
        error_response._content = str({"error": "Failed to process image", "details": str(e)}).encode('utf-8')
        return error_response

def NumberImagesProcessedByDate(token: str) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/model/process_images_by_date", headers=headers)

    return response

def DetectedAndMissingProducts(token: str,id_image:int) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/model/detected_and_missing_products?id_image={id_image}", headers=headers)

    return response

def TotalProductsDetected(token: str,id_image:int) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/model/total_products_detected?id_image={id_image}", headers=headers)

    return response

def ImageDetectionReport(token: str,id_image:int) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/model/image_detection_report?id_image={id_image}", headers=headers)

    return response

def ImageDetectionAll(token: str,start_date: str, end_date: str) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.get(f"{API_BASE_URL}/model/image_detection_all", headers=headers, params=params)
    
    return response

def ImageS3(token: str,s3_url:str) -> requests.Response:
    """
    This function calls the API to get the number of images processed per day.

    Args:
        token (str): token to authenticate the user

    Returns:
        requests.Response: response from the API
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/model/image_s3?s3_url={s3_url}", headers=headers)

    return response