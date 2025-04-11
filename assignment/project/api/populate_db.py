import psycopg2
from app import settings as config
from app.db import Base
from app.user.models import User
from app.image.models import Image, DetectedProduct, MissingProduct, ImageProcessingLog
from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_USERNAME = config.DATABASE_USERNAME
DATABASE_PASSWORD = config.DATABASE_PASSWORD
DATABASE_HOST = config.DATABASE_HOST
DATABASE_NAME = config.DATABASE_NAME
DATABASE_PORT = config.DATABASE_PORT

# Create the initial connection URL to PostgreSQL (without specifying the database)
initial_connection_url = (
    f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/postgres"
)

print(initial_connection_url)

conn = None

# Connect to PostgreSQL to create the database if it doesn't exist
try:
    conn = psycopg2.connect(initial_connection_url)
    conn.autocommit = True
    cursor = conn.cursor()


    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DATABASE_NAME}'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
        print(f"Base de datos '{DATABASE_NAME}' creada exitosamente.")
    else:
        print(f"La base de datos '{DATABASE_NAME}' ya existe.")

except Exception as e:
    print(f"Error al conectar/crear la base de datos: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
print(f"Conectando a la base de datos: {SQLALCHEMY_DATABASE_URL}")


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


Base.metadata.create_all(engine)
print("✅ Tablas verificadas y creadas si no existían.")


Session = sessionmaker(bind=engine)
session = Session()


if not session.query(User).first():
    user = User(
        name="Admin User",
        password="admin",
        email="admin@example.com",
    )
    session.add(user)
    session.commit()
    print("🟢 Usuario por defecto agregado.")

session.close()
print("✅ Configuración de base de datos finalizada con éxito.")