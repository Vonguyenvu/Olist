import os
from db_connection import get_db_engine
import pandas as pd

engine = get_db_engine()

def clean_customers():
    print("🧹 [Silver] Cleaning customers...")
    # Đọc từ bronze schema
    df = pd.read_sql("SELECT * FROM bronze.customers", engine)
    
    # Làm sạch: loại bỏ khoảng trắng thừa
    df['customer_city'] = df['customer_city'].str.strip().str.title()
    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    
    # Ghi trực tiếp vào silver schema trong Postgres
    df.to_sql("customers", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.customers")

def clean_products():
    print("🧹 [Silver] Cleaning products...")
    df = pd.read_sql("SELECT * FROM bronze.products", engine)
    
    # Ép kiểu dữ liệu số
    numeric_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    df.to_sql("products", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.products")

def clean_sellers():
    print("🧹 [Silver] Cleaning sellers...")
    df = pd.read_sql("SELECT * FROM bronze.sellers", engine)
    
    df['seller_city'] = df['seller_city'].str.strip().str.title()
    df['seller_state'] = df['seller_state'].str.strip().str.upper()
    
    df.to_sql("sellers", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.sellers")

def clean_reviews():
    print("🧹 [Silver] Cleaning reviews & deduplicating...")
    df = pd.read_sql("SELECT * FROM bronze.order_reviews", engine)
    
    # Parse timestamp
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"])
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"])
    
    # Khử trùng lặp (giữ lại review mới nhất cho từng review_id)
    df = df.sort_values("review_answer_timestamp").groupby("review_id").last().reset_index()
    
    # Xử lý text NULL
    df["review_comment_title"] = df["review_comment_title"].fillna("No Title").str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("No Comment").str.strip()
    
    df.to_sql("reviews", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.reviews")

def clean_orders():
    print("🧹 [Silver] Cleaning orders & parsing dates...")
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
    print("🧹 [Silver] Cleaning order items...")
    df = pd.read_sql("SELECT * FROM bronze.order_items", engine)
    
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"])
    df["price"] = pd.to_numeric(df["price"], errors='coerce').fillna(0.0)
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("order_items", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.order_items")

def clean_payments():
    print("🧹 [Silver] Cleaning payments...")
    df = pd.read_sql("SELECT * FROM bronze.order_payments", engine)
    
    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"]).astype(int)
    df["payment_installments"] = pd.to_numeric(df["payment_installments"]).astype(int)
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors='coerce').fillna(0.0)
    
    df.to_sql("payments", engine, schema="silver", if_exists="replace", index=False)
    print("   -> Saved to silver.payments")

def run_bronze_to_silver():
    print("🚀 === BẮT ĐẦU CHẠY TẦNG BRONZE -> SILVER (POSTGRESQL) ===")
    clean_customers()
    clean_products()
    clean_sellers()
    clean_reviews()
    clean_orders()
    clean_order_items()
    clean_payments()
    print("✅ ĐÃ LÀM SẠCH VÀ NẠP DỮ LIỆU THÀNH CÔNG VÀO SCHEMA SILVER!\n")

if __name__ == "__main__":
    run_bronze_to_silver()
    
    

