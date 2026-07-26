import logging
from sqlalchemy import text
import pandas as pd

from .db_connection import get_db_engine
from logging_setup import setup_logging

engine = get_db_engine()
logger = logging.getLogger(__name__)


def create_silver_schema(engine):
    """Đảm bảo schema silver đã được khởi tạo trong PostgreSQL"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        conn.commit()
    logger.info("Schema silver sẵn sàng")


def clear_existing_silver_tables(engine):
    """Xóa dữ liệu cũ trong schema silver trước khi nạp mới."""
    logger.info("Đang làm sạch schema silver")

    tables = [
        "customers",
        "products",
        "sellers",
        "order_reviews",
        "orders",
        "order_items",
        "order_payments",
        "geolocation",
        "product_category_name_translation",
    ]

    with engine.connect() as conn:
        for table_name in tables:
            try:
                conn.execute(text(f"TRUNCATE TABLE silver.{table_name};"))
            except Exception:
                logger.warning("Không thể TRUNCATE silver.%s; có thể bảng chưa được tạo", table_name, exc_info=True)
        conn.commit()

    logger.info("Đã làm sạch schema silver")

def clean_customers():
    logger.info("Đang làm sạch bronze.customers")
    df = pd.read_sql('SELECT * FROM bronze.customers', engine)
    
    # Làm sạch: loại bỏ khoảng trắng thừa
    df['customer_city'] = df['customer_city'].str.strip().str.title()
    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    df["customer_zip_code_prefix"] = pd.to_numeric(df["customer_zip_code_prefix"], errors="coerce").astype("Int64")
    df.to_sql(name = "customers", con= engine, schema= 'silver', if_exists='append', index= False)
    logger.info("Đã nạp %d dòng vào silver.customers", len(df))

def clean_products():
    logger.info("Đang làm sạch bronze.products")
    df = pd.read_sql(sql='SELECT * FROM bronze.products', con= engine)
    
    # Ép kiểu dữ liệu số
    numeric_cols = ["product_description_lenght","product_photos_qty","product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    df.to_sql(name='products', con= engine,schema='silver', if_exists='append', index=False)
    logger.info("Đã nạp %d dòng vào silver.products", len(df))

def clean_sellers():
    logger.info("Đang làm sạch bronze.sellers")
    df = pd.read_sql("SELECT * FROM bronze.sellers", engine)
    
    # Làm sạch: loại bỏ khoảng trắng thừa
    df['seller_city'] = df['seller_city'].str.strip().str.title()
    df['seller_state'] = df['seller_state'].str.strip().str.upper()
    df["seller_zip_code_prefix"] = pd.to_numeric(df["seller_zip_code_prefix"], errors="coerce").astype("Int64")
    
    df.to_sql("sellers", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.sellers", len(df))

def clean_reviews():
    logger.info("Đang làm sạch bronze.order_reviews")
    df = pd.read_sql("SELECT * FROM bronze.order_reviews", engine)
    
    # Parse timestamp
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"],errors='coerce')
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"],errors='coerce')
    
    # Khử trùng lặp (giữ lại review mới nhất cho từng review_id)
    df = df.sort_values("review_answer_timestamp").groupby("review_id").last().reset_index()
    
    # Ép kiểu dữ liệu số
    df["review_score"] = pd.to_numeric(df["review_score"],errors='coerce').astype("Int64")
    
    # Xử lý text NULL
    df["review_comment_title"] = df["review_comment_title"].fillna("No Title").str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("No Comment").str.strip()
    
    df.to_sql("order_reviews", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.order_reviews", len(df))

def clean_orders():
    logger.info("Đang làm sạch bronze.orders")
    df = pd.read_sql("SELECT * FROM bronze.orders", engine)
    
    # Ép kiểu Datetime cho tất cả các cột thời gian
    date_cols = [
        "order_purchase_timestamp", "order_approved_at", 
        "order_delivered_carrier_date", "order_delivered_customer_date", 
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    df.to_sql("orders", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.orders", len(df))

def clean_order_items():
    logger.info("Đang làm sạch bronze.order_items")
    df = pd.read_sql("SELECT * FROM bronze.order_items", engine)
    
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"])
    df["price"] = pd.to_numeric(df["price"], errors='coerce').fillna(0.0)
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("order_items", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.order_items", len(df))

def clean_payments():
    logger.info("Đang làm sạch bronze.order_payments")
    df = pd.read_sql("SELECT * FROM bronze.order_payments", engine)
    
    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"],errors='coerce').astype("Int64")
    df["payment_installments"] = pd.to_numeric(df["payment_installments"],errors='coerce').astype("Int64")
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("order_payments", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.order_payments", len(df))

def clean_geolocation():
    logger.info("Đang làm sạch bronze.geolocation")
    df = pd.read_sql("SELECT * FROM bronze.geolocation", engine)
    
    # Ép kiểu tọa độ và làm sạch text
    df['geolocation_zip_code_prefix'] = pd.to_numeric(df['geolocation_zip_code_prefix'], errors='coerce').astype('Int64')
    df['geolocation_lat'] = pd.to_numeric(df['geolocation_lat'], errors='coerce')
    df['geolocation_lng'] = pd.to_numeric(df['geolocation_lng'], errors='coerce')
    df['geolocation_city'] = df['geolocation_city'].str.strip().str.title()
    df['geolocation_state'] = df['geolocation_state'].str.strip().str.upper()
    
    # Loại bỏ trùng lặp hoàn toàn
    df = df.drop_duplicates()
    
    df.to_sql("geolocation", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.geolocation", len(df))

def clean_translation():
    logger.info("Đang làm sạch bronze.product_category_name_translation")
    df = pd.read_sql("SELECT * FROM bronze.product_category_name_translation", engine)
    df['product_category_name'] = df['product_category_name'].str.strip()
    df['product_category_name_english'] = df['product_category_name_english'].str.strip()
    
    # Loại bỏ trùng lặp hoàn toàn
    df = df.drop_duplicates()
    
    df.to_sql("product_category_name_translation", engine, schema="silver", if_exists="append", index=False)
    logger.info("Đã nạp %d dòng vào silver.product_category_name_translation", len(df))
    
def run_bronze_to_silver():
    logger.info("Bắt đầu tầng bronze -> silver")
    try:
        create_silver_schema(engine)
        clear_existing_silver_tables(engine)
        clean_customers()
        clean_products()
        clean_sellers()
        clean_reviews()
        clean_orders()
        clean_order_items()
        clean_payments()
        clean_geolocation()
        clean_translation()
        logger.info("Hoàn thành tầng bronze -> silver")
    except Exception:
        logger.exception("Tầng bronze -> silver thất bại")
        raise

if __name__ == "__main__":
    setup_logging()
    run_bronze_to_silver()
    
    
