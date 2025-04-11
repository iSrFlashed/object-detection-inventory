from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Image(Base):
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    image_name = Column(String(255), nullable=False)
    s3_url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    detected_products = relationship("DetectedProduct", back_populates="image", cascade="all, delete")
    missing_products = relationship("MissingProduct", back_populates="image", cascade="all, delete")
    logs = relationship("ImageProcessingLog", back_populates="image", cascade="all, delete")


class DetectedProduct(Base):
    __tablename__ = "detected_products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    image = relationship("Image", back_populates="detected_products")


class MissingProduct(Base):
    __tablename__ = "missing_products"

    missing_id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    image = relationship("Image", back_populates="missing_products")


class ImageProcessingLog(Base):
    __tablename__ = "image_processing_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"), nullable=False)
    log_message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    image = relationship("Image", back_populates="logs")
