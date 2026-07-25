import os
from sqlalchemy import text
from db_connection import get_db_engine
import pandas as pd

engine = get_db_engine()


def create_silver_schema(engine):
    """Đảm bảo schema silver đã được khởi tạo trong PostgreSQL"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        conn.commit()
    print("✅ Đã kiểm tra/khởi tạo schema 'silver'.")


def clear_existing_silver_tables(engine):
    """Xóa dữ liệu cũ trong schema silver trước khi nạp mới."""
    print("Đang làm sạch dữ liệu cũ trong schema silver...")

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
            except Exception as exc:
                print(f"ℹBỏ qua TRUNCATE silver.{table_name} (có thể bảng chưa được tạo): {exc}")
        conn.commit()

    print("   ✅ Đã làm sạch dữ liệu cũ trong schema silver.\n")

def clean_customers():
    print("[Silver] Cleaning customers...")
    # Đọc từ bronze schema
    df = pd.read_sql("SELECT * FROM bronze.customers", engine)
    
    # Làm sạch: loại bỏ khoảng trắng thừa
    df['customer_city'] = df['customer_city'].str.strip().str.title()
    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    
    # Ghi trực tiếp vào silver schema trong Postgres
    df.to_sql("customers", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.customers")

def clean_products():
    print("[Silver] Cleaning products...")
    df = pd.read_sql("SELECT * FROM bronze.products", engine)
    
    # Ép kiểu dữ liệu số
    numeric_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    df.to_sql("products", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.products")

def clean_sellers():
    print("[Silver] Cleaning sellers...")
    df = pd.read_sql("SELECT * FROM bronze.sellers", engine)
    
    df['seller_city'] = df['seller_city'].str.strip().str.title()
    df['seller_state'] = df['seller_state'].str.strip().str.upper()
    
    df.to_sql("sellers", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.sellers")

def clean_reviews():
    print("[Silver] Cleaning reviews & deduplicating...")
    df = pd.read_sql("SELECT * FROM bronze.order_reviews", engine)
    
    # Parse timestamp
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"])
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"])
    
    # Khử trùng lặp (giữ lại review mới nhất cho từng review_id)
    df = df.sort_values("review_answer_timestamp").groupby("review_id").last().reset_index()
    
    # Xử lý text NULL
    df["review_comment_title"] = df["review_comment_title"].fillna("No Title").str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("No Comment").str.strip()
    
    df.to_sql("order_reviews", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.order_reviews")

def clean_orders():
    print("[Silver] Cleaning orders & parsing dates...")
    df = pd.read_sql("SELECT * FROM bronze.orders", engine)
    
    # Ép kiểu Datetime cho tất cả các cột thời gian
    date_cols = [
        "order_purchase_timestamp", "order_approved_at", 
        "order_delivered_carrier_date", "order_delivered_customer_date", 
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
        
    df.to_sql("orders", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.orders")

def clean_order_items():
    print("[Silver] Cleaning order items...")
    df = pd.read_sql("SELECT * FROM bronze.order_items", engine)
    
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"])
    df["price"] = pd.to_numeric(df["price"], errors='coerce').fillna(0.0)
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("order_items", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.order_items")

def clean_payments():
    print("[Silver] Cleaning payments...")
    df = pd.read_sql("SELECT * FROM bronze.order_payments", engine)
    
    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"]).astype(int)
    df["payment_installments"] = pd.to_numeric(df["payment_installments"]).astype(int)
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("order_payments", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.order_payments")

def clean_geolocation():
    print("[Silver] Cleaning geolocation...")
    df = pd.read_sql("SELECT * FROM bronze.geolocation", engine)
    
    # Ép kiểu tọa độ và làm sạch text
    df['geolocation_zip_code_prefix'] = pd.to_numeric(df['geolocation_zip_code_prefix'], errors='coerce').astype('Int64')
    df['geolocation_lat'] = pd.to_numeric(df['geolocation_lat'], errors='coerce')
    df['geolocation_lng'] = pd.to_numeric(df['geolocation_lng'], errors='coerce')
    df['geolocation_city'] = df['geolocation_city'].str.strip().str.title()
    df['geolocation_state'] = df['geolocation_state'].str.strip().str.upper()
    
    # Loại bỏ trùng lặp hoàn toàn
    df = df.drop_duplicates()
    
    df.to_sql("geolocation", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.geolocation")

def clean_translation():
    print("[Silver] Cleaning category translation...")
    df = pd.read_sql("SELECT * FROM bronze.product_category_name_translation", engine)
    df['product_category_name'] = df['product_category_name'].str.strip()
    df['product_category_name_english'] = df['product_category_name_english'].str.strip()
    
    # Loại bỏ trùng lặp hoàn toàn
    df = df.drop_duplicates()
    
    df.to_sql("product_category_name_translation", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.product_category_name_translation")
    
def run_bronze_to_silver():
    create_silver_schema(engine)
    clear_existing_silver_tables(engine)
    print(" === BẮT ĐẦU CHẠY TẦNG BRONZE -> SILVER (POSTGRESQL) ===")
    clean_customers()
    clean_products()
    clean_sellers()
    clean_reviews()
    clean_orders()
    clean_order_items()
    clean_payments()
    clean_geolocation()
    clean_translation()
    print("✅ ĐÃ LÀM SẠCH VÀ NẠP DỮ LIỆU THÀNH CÔNG VÀO SCHEMA SILVER!\n")

if __name__ == "__main__":
    run_bronze_to_silver()
    
    

