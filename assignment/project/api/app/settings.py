import os

# import dotenv
import dotenv

# Load environment variables from .env file

dotenv.load_dotenv()

# Run API in Debug mode
API_DEBUG = True

# We will store images uploaded by the user on this folder
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# REDIS settings
# Queue name
REDIS_QUEUE = "service_queue"
# Port
REDIS_PORT = 6379
# DB Id
REDIS_DB_ID = 0
# Host IP
REDIS_IP = os.getenv("REDIS_IP", "redis")
# Sleep parameters which manages the
# interval between requests to our redis queue
API_SLEEP = 0.05

# Database settings
DATABASE_USERNAME = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("POSTGRES_DB")
DATABASE_PORT = os.getenv("POSTGRES_PORT")
SECRET_KEY = os.getenv("SECRET_KEY", "S09WWWHXBAJDIUEREHCN3752346572452VGGGVWWW526194")

AWS_ACCESS_KEY_ID_OUTPUT=os.getenv("AWS_ACCESS_KEY_ID_OUTPUT")
AWS_SECRET_ACCESS_KEY_OUTPUT=os.getenv("AWS_SECRET_ACCESS_KEY_OUTPUT")
AWS_SESSION_TOKEN_OUTPUT=os.getenv("AWS_SESSION_TOKEN_OUTPUT")
S3_BUCKET_NAME_OUTPUT=os.getenv("S3_BUCKET_NAME_OUTPUT")
S3_BUCKET_PREFIX_OUTPUT=os.getenv("S3_BUCKET_PREFIX_OUTPUT")
