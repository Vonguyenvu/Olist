import os
import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

def create_analytics_schema(engine):
    """Đảm bảo schema analytics (Gold) đã được tạo"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        
        conn.commit()
    print("✅ Đã kiểm tra/khởi tạo schema 'silver'.")

def build_dim_customers(engine):
    print("🏆 [Gold] Building dim_customers...")
    df = pd.read_sql("SELECT * FROM silver.customers", engine)
    
    dim_customers = pd.DataFrame({
        "customer_key": df["customer_id"],
        "customer_unique_id": df["customer_unique_id"],
        "customer_zip_code_prefix": pd.to_numeric(df["customer_zip_code_prefix"], errors="coerce").astype("Int64"),
        "customer_city": df["customer_city"],
        "customer_state": df["customer_state"]
    })
    
    dim_customers.to_sql("dim_customers", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_customers")

def build_dim_products(engine):
    print("🏆 [Gold] Building dim_products (kèm dịch tên danh mục)...")
    products_df = pd.read_sql("SELECT * FROM silver.products", engine)
    trans_df = pd.read_sql("SELECT * FROM bronze.product_category_name_translation", engine)
    
    # Merge với bảng translation từ bronze
    merged = products_df.merge(trans_df, on="product_category_name", how="left")
    
    dim_products = pd.DataFrame({
        "product_key": merged["product_id"],
        "product_category_name_pt": merged["product_category_name"],
        "product_category_name_en": merged["product_category_name_english"],
        "product_weight_g": pd.to_numeric(merged["product_weight_g"], errors="coerce").fillna(0).astype(int),
        "product_length_cm": pd.to_numeric(merged["product_length_cm"], errors="coerce").fillna(0).astype(int),
        "product_height_cm": pd.to_numeric(merged["product_height_cm"], errors="coerce").fillna(0).astype(int),
        "product_width_cm": pd.to_numeric(merged["product_width_cm"], errors="coerce").fillna(0).astype(int)
    })
    
    dim_products.to_sql("dim_products", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_products")

def build_dim_sellers(engine):
    print("🏆 [Gold] Building dim_sellers...")
    df = pd.read_sql("SELECT * FROM silver.sellers", engine)
    
    dim_sellers = pd.DataFrame({
        "seller_key": df["seller_id"],
        "seller_zip_code_prefix": pd.to_numeric(df["seller_zip_code_prefix"], errors="coerce").astype("Int64"),
        "seller_city": df["seller_city"],
        "seller_state": df["seller_state"]
    })
    
    dim_sellers.to_sql("dim_sellers", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_sellers")

def build_dim_reviews(engine):
    print("🏆 [Gold] Building dim_reviews...")
    df = pd.read_sql("SELECT * FROM silver.reviews", engine)
    
    dim_reviews = pd.DataFrame({
        "review_key": df["review_id"],
        "review_score": pd.to_numeric(df["review_score"], errors="coerce").astype("Int64"),
        "review_comment_title": df["review_comment_title"],
        "review_comment_message": df["review_comment_message"],
        "review_creation_date": pd.to_datetime(df["review_creation_date"]),
        "review_answer_timestamp": pd.to_datetime(df["review_answer_timestamp"]),
        "has_comment": df["review_comment_message"].notna() & (df["review_comment_message"] != "No Comment")
    })
    
    dim_reviews.to_sql("dim_reviews", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_reviews")

def build_dim_payment_types(engine):
    print("🏆 [Gold] Building dim_payment_types...")
    df = pd.read_sql("SELECT DISTINCT payment_type FROM silver.payments", engine)
    
    dim_payment_types = pd.DataFrame({
        "payment_type_key": df["payment_type"],
        "payment_type_name": df["payment_type"]
    })
    
    dim_payment_types.to_sql("dim_payment_types", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_payment_types")

def build_dim_date(engine):
    print("🏆 [Gold] Building dim_date (Tự động sinh ngày lịch)...")
    orders_df = pd.read_sql("SELECT order_purchase_timestamp FROM silver.orders", engine)
    orders_df["purchase_dt"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    
    min_date = orders_df["purchase_dt"].min().floor("D")
    max_date = orders_df["purchase_dt"].max().ceil("D") + pd.Timedelta(days=90) # Mở rộng khoảng thời gian
    
    date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    dim_date = pd.DataFrame({
        "date_key": date_range.strftime("%Y%m%d").astype(int),
        "full_date": date_range.date,
        "year": date_range.year,
        "quarter": date_range.quarter,
        "month": date_range.month,
        "month_name": date_range.strftime("%B"),
        "day_of_week": date_range.dayofweek + 1,
        "is_weekend": date_range.dayofweek >= 5
    })
    
    dim_date.to_sql("dim_date", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.dim_date")

def build_fact_payments(engine):
    print("🏆 [Gold] Building fact_payments...")
    payments_df = pd.read_sql("SELECT * FROM silver.payments", engine)
    orders_df = pd.read_sql("SELECT order_id, customer_id FROM silver.orders", engine)
    
    # Ghép lấy customer_id cho fact_payments
    merged = payments_df.merge(orders_df, on="order_id", how="left")
    
    fact_payments = pd.DataFrame({
        "payment_id": merged["order_id"] + "-" + merged["payment_sequential"].astype(str),
        "order_id": merged["order_id"],
        "customer_key": merged["customer_id"],
        "payment_type_key": merged["payment_type"],
        "payment_sequential": pd.to_numeric(merged["payment_sequential"], errors="coerce").astype("Int64"),
        "payment_installments": pd.to_numeric(merged["payment_installments"], errors="coerce").astype("Int64"),
        "payment_value": pd.to_numeric(merged["payment_value"], errors="coerce").fillna(0.0)
    })
    
    fact_payments.to_sql("fact_payments", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.fact_payments")

def build_fact_orders(engine):
    print("🏆 [Gold] Building fact_orders...")
    items_df = pd.read_sql("SELECT * FROM silver.order_items", engine)
    orders_df = pd.read_sql("SELECT * FROM silver.orders", engine)
    reviews_df = pd.read_sql("SELECT review_id, order_id FROM silver.reviews", engine)
    
    # Join items với orders
    df = items_df.merge(orders_df, on="order_id", how="inner")
    
    # Left join với reviews (1 order có thể có hoặc chưa có review)
    df = df.merge(reviews_df, on="order_id", how="left")
    
    # Chuyển đổi timestamp
    purchase_dt = pd.to_datetime(df["order_purchase_timestamp"])
    delivered_dt = pd.to_datetime(df["order_delivered_customer_date"])
    estimated_dt = pd.to_datetime(df["order_estimated_delivery_date"])
    
    price = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    freight = pd.to_numeric(df["freight_value"], errors="coerce").fillna(0.0)
    
    delivery_actual = (delivered_dt - purchase_dt).dt.days
    delivery_est = (estimated_dt - purchase_dt).dt.days
    
    fact_orders = pd.DataFrame({
        "order_item_key": df["order_id"] + "-" + df["order_item_id"].astype(str),
        "order_id": df["order_id"],
        "customer_key": df["customer_id"],
        "product_key": df["product_id"],
        "seller_key": df["seller_id"],
        "review_key": df["review_id"],
        "order_purchase_date_key": purchase_dt.dt.strftime("%Y%m%d").astype("Int64"),
        "order_delivered_date_key": delivered_dt.dt.strftime("%Y%m%d").astype("Int64"),
        "order_status": df["order_status"],
        "is_delayed": delivered_dt > estimated_dt,
        "price": price,
        "freight_value": freight,
        "total_item_value": price + freight,
        "delivery_days_actual": delivery_actual,
        "delivery_days_estimated": delivery_est
    })
    
    fact_orders.to_sql("fact_orders", engine, schema="analytics", if_exists="append", index=False)
    print("   -> Loaded analytics.fact_orders")

def clear_existing_gold_tables(engine):
    """Xóa dữ liệu cũ trong các bảng Gold trước khi nạp mới (để tránh lỗi trùng khóa)"""
    tables = [
        "analytics.fact_orders", "analytics.fact_payments",
        "analytics.dim_customers", "analytics.dim_products", 
        "analytics.dim_sellers", "analytics.dim_reviews", 
        "analytics.dim_payment_types", "analytics.dim_date"
    ]
    with engine.connect() as conn:
        for tbl in tables:
            conn.execute(text(f"TRUNCATE TABLE {tbl} CASCADE;"))
        conn.commit()
    print("🧹 Đã làm sạch các bảng cũ trong schema analytics.")

def run_silver_to_gold():
    engine = get_db_engine()
    create_analytics_schema(engine)
    
    print("\n🚀 === BẮT ĐẦU CHẠY TẦNG SILVER -> GOLD (ANALYTICS SCHEMA) ===")
    
    # Xóa dữ liệu cũ nếu có
    try:
        clear_existing_gold_tables(engine)
    except Exception as e:
        print(f"ℹ️ Bỏ qua bước TRUNCATE (có thể các bảng chưa được tạo): {e}")

    # 1. Nạp các bảng Dimension trước
    build_dim_customers(engine)
    build_dim_products(engine)
    build_dim_sellers(engine)
    build_dim_reviews(engine)
    build_dim_payment_types(engine)
    build_dim_date(engine)
    
    # 2. Nạp các bảng Fact sau
    build_fact_payments(engine)
    build_fact_orders(engine)
    
    print("\n🎉 ĐÃ CHUYỂN ĐỔI THÀNH CÔNG DỮ LIỆU SANG STAR SCHEMA TRONG SCHEMA ANALYTICS!\n")

if __name__ == "__main__":
    run_silver_to_gold()