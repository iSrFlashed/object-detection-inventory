import os
import boto3
import concurrent.futures
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '../configs/.env'))  # Specify the path to the .env file


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME  = os.getenv("S3_BUCKET_NAME")
PREFIX       = os.getenv("S3_BUCKET_PREFIX")
LOCAL_DIR    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
image_folder = os.path.join(LOCAL_DIR , 'images')
csv_folder   = os.path.join(LOCAL_DIR , 'csv')
test_folder  = os.path.join(image_folder, 'test')
train_folder = os.path.join(image_folder, 'train')
val_folder   = os.path.join(image_folder, 'val')



s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(image_folder, exist_ok=True)
os.makedirs(csv_folder, exist_ok=True)
os.makedirs(test_folder, exist_ok=True)
os.makedirs(train_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)

def list_all_files():
    """
    List all files within the S3 bucket under a specific prefix.
    """
    continuation_token = None
    all_files = []

    while True:
        list_kwargs = {"Bucket": BUCKET_NAME, "Prefix": PREFIX}
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**list_kwargs)

        if "Contents" in response:
            all_files.extend([obj["Key"] for obj in response["Contents"]])

        if response.get("IsTruncated"):  # If there are more files, continue paging
            continuation_token = response["NextContinuationToken"]
        else:
            break

    return all_files

def download_file(s3_file_key):
    """
    Download a single file from S3.
    """
    file_name = os.path.basename(s3_file_key)
   
    if file_name.endswith('.jpg'):
        if file_name.startswith('test'):
            destination_folder = test_folder
        elif file_name.startswith('train'):
            destination_folder = train_folder
        elif file_name.startswith('val'):
            destination_folder = val_folder
        else:
            destination_folder = image_folder
    elif file_name.endswith('.csv'):
        destination_folder = csv_folder
    else:
        destination_folder = LOCAL_DIR  # Otros archivos quedan en 'dataset/'

    local_file_path = os.path.join(destination_folder, file_name)

    try:
        s3_client.download_file(BUCKET_NAME, s3_file_key, local_file_path)
        print(f"✅ Downloaded: {file_name}")
    except Exception as e:
        print(f"❌ Error downloading {file_name}: {e}")

def download_all_files_parallel(max_workers=10):
    """
    Download all files from S3 in parallel using threads.
    """
    all_files = list_all_files()
    print(f"🔹 Total de archivos a descargar: {len(all_files)}")


    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(download_file, all_files)

    print("✅ Download completed.")

if __name__ == "__main__":
    download_all_files_parallel(max_workers=10)
