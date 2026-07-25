import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

def create_gold_schema(engine):
    """Đảm bảo schema gold đã được khởi tạo trong PostgreSQL"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold;"))
        conn.commit()
    print("Schema 'gold' sẵn sàng.")

def clear_existing_gold_tables(engine):
    """
    Xóa dữ liệu cũ trong schema gold trước khi nạp mới.
    LƯU Ý THỨ TỰ: TRUNCATE các bảng Fact trước, bảng Dim sau!
    """
    print("Đang làm sạch schema gold...")
    
    fact_tables = [
        "gold.fact_orders", 
        "gold.fact_payments"
    ]
    
    dim_tables = [
        "gold.dim_customers", 
        "gold.dim_products", 
        "gold.dim_sellers", 
        "gold.dim_reviews", 
        "gold.dim_payment_types", 
        "gold.dim_date"
    ]
    
    with engine.connect() as conn:
        # Xóa các bảng Fact trước
        for tbl in fact_tables:
            conn.execute(text(f"TRUNCATE TABLE {tbl} CASCADE;"))
            
        # Xóa các bảng Dim sau
        for tbl in dim_tables:
            conn.execute(text(f"TRUNCATE TABLE {tbl} CASCADE;"))
            
        conn.commit()
    print("-> Đã làm sạch schema gold.\n")

def load_silver_data(engine):
    """Đọc dữ liệu đã làm sạch từ schema silver trong PostgreSQL"""
    print("Đang đọc dữ liệu từ Schema Silver...")
    
    customers_df = pd.read_sql("SELECT * FROM silver.customers", engine)
    products_df = pd.read_sql("SELECT * FROM silver.products", engine)
    sellers_df = pd.read_sql("SELECT * FROM silver.sellers", engine)
    reviews_df = pd.read_sql("SELECT * FROM silver.order_reviews", engine)
    payments_df = pd.read_sql("SELECT * FROM silver.order_payments", engine)
    orders_df = pd.read_sql("SELECT * FROM silver.orders", engine)
    order_items_df = pd.read_sql("SELECT * FROM silver.order_items", engine)
    
    translation_df = pd.read_sql("SELECT * FROM silver.product_category_name_translation", engine)
    
    return {
        "customers": customers_df,
        "products": products_df,
        "sellers": sellers_df,
        "reviews": reviews_df,
        "payments": payments_df,
        "orders": orders_df,
        "order_items": order_items_df,
        "translation": translation_df
    }

def transform_and_load_dims(silver_data, engine):
    """Biến đổi và Load dữ liệu vào các bảng Dimension (Schema GOLD)"""
    print("Đang biến đổi và nạp dữ liệu vào các bảng Dimension...")

    # 1. dim_customers
    dim_customers = silver_data["customers"][[
        "customer_id", "customer_unique_id", "customer_zip_code_prefix", 
        "customer_city", "customer_state"
    ]].rename(columns={"customer_id": "customer_key"})
    
    dim_customers["customer_zip_code_prefix"] = pd.to_numeric(dim_customers["customer_zip_code_prefix"], errors="coerce").astype("Int64")
    dim_customers.to_sql("dim_customers", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_customers")

    # 2. dim_products (Kết hợp dịch tên danh mục)
    products_merged = silver_data["products"].merge(
        silver_data["translation"], 
        on="product_category_name", 
        how="left"
    )
    dim_products = pd.DataFrame({
        "product_key": products_merged["product_id"],
        "product_category_name_pt": products_merged["product_category_name"],
        "product_category_name_en": products_merged["product_category_name_english"],
        "product_weight_g": pd.to_numeric(products_merged["product_weight_g"], errors="coerce").fillna(0).astype(int),
        "product_length_cm": pd.to_numeric(products_merged["product_length_cm"], errors="coerce").fillna(0).astype(int),
        "product_height_cm": pd.to_numeric(products_merged["product_height_cm"], errors="coerce").fillna(0).astype(int),
        "product_width_cm": pd.to_numeric(products_merged["product_width_cm"], errors="coerce").fillna(0).astype(int)
    })
    dim_products.to_sql("dim_products", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_products")

    # 3. dim_sellers
    dim_sellers = silver_data["sellers"][[
        "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"
    ]].rename(columns={"seller_id": "seller_key"})
    
    dim_sellers["seller_zip_code_prefix"] = pd.to_numeric(dim_sellers["seller_zip_code_prefix"], errors="coerce").astype("Int64")
    dim_sellers.to_sql("dim_sellers", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_sellers")

    # 4. dim_reviews
    reviews_df = silver_data["reviews"].copy()
    dim_reviews = pd.DataFrame({
        "review_key": reviews_df["review_id"],
        "review_score": pd.to_numeric(reviews_df["review_score"], errors="coerce").astype("Int64"),
        "review_comment_title": reviews_df["review_comment_title"],
        "review_comment_message": reviews_df["review_comment_message"],
        "review_creation_date": pd.to_datetime(reviews_df["review_creation_date"]),
        "review_answer_timestamp": pd.to_datetime(reviews_df["review_answer_timestamp"]),
        "has_comment": reviews_df["review_comment_message"].notna() & (reviews_df["review_comment_message"] != "No Comment")
    })
    dim_reviews.to_sql("dim_reviews", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_reviews")

    # 5. dim_payment_types
    unique_payment_types = silver_data["payments"]["payment_type"].dropna().unique()
    dim_payment_types = pd.DataFrame({
        "payment_type_key": unique_payment_types,
        "payment_type_name": unique_payment_types
    })
    dim_payment_types.to_sql("dim_payment_types", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_payment_types")

    # 6. dim_date
    orders_df = silver_data["orders"].copy()
    orders_df["purchase_dt"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    
    min_date = orders_df["purchase_dt"].min().floor("D")
    max_date = orders_df["purchase_dt"].max().ceil("D") + pd.Timedelta(days=90)
    
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
    dim_date.to_sql("dim_date", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.dim_date")

def transform_and_load_facts(silver_data, engine):
    """Biến đổi và Load dữ liệu vào các bảng Fact (Schema GOLD)"""
    print("Đang biến đổi và nạp dữ liệu vào các bảng Fact...")

    # A. fact_payments
    payments_df = silver_data["payments"].copy()
    payments_df["payment_id"] = payments_df["order_id"] + "-" + payments_df["payment_sequential"].astype(str)
    
    orders_df = silver_data["orders"][["order_id", "customer_id"]]
    payments_merged = payments_df.merge(orders_df, on="order_id", how="left")

    fact_payments = pd.DataFrame({
        "payment_id": payments_merged["payment_id"],
        "order_id": payments_merged["order_id"],
        "customer_key": payments_merged["customer_id"],
        "payment_type_key": payments_merged["payment_type"],
        "payment_sequential": pd.to_numeric(payments_merged["payment_sequential"], errors="coerce").astype("Int64"),
        "payment_installments": pd.to_numeric(payments_merged["payment_installments"], errors="coerce").astype("Int64"),
        "payment_value": pd.to_numeric(payments_merged["payment_value"], errors="coerce").fillna(0.0)
    })
    fact_payments.to_sql("fact_payments", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.fact_payments")

    # B. fact_orders
    items_df = silver_data["order_items"].copy()
    orders_df = silver_data["orders"].copy()
    reviews_df = silver_data["reviews"].copy()

    # KHỬ TRÙNG LẶP REVIEWS: Đảm bảo 1 order_id chỉ lấy 1 review_id mới nhất
    reviews_dedup = (
        reviews_df.sort_values("review_answer_timestamp")
        .groupby("order_id")
        .last()
        .reset_index()[["order_id", "review_id"]]
    )

    # Ghép bảng items với orders và reviews_dedup
    df = items_df.merge(orders_df, on="order_id", how="inner")
    df = df.merge(reviews_dedup, on="order_id", how="left")

    # Chuyển đổi datetime
    df["purchase_dt"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["delivered_dt"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["estimated_dt"] = pd.to_datetime(df["order_estimated_delivery_date"])

    # Tính toán chỉ số delivery
    df["delivery_days_actual"] = (df["delivered_dt"] - df["purchase_dt"]).dt.days
    df["delivery_days_estimated"] = (df["estimated_dt"] - df["purchase_dt"]).dt.days
    df["is_delayed"] = df["delivered_dt"] > df["estimated_dt"]

    price = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    freight = pd.to_numeric(df["freight_value"], errors="coerce").fillna(0.0)

    fact_orders = pd.DataFrame({
        "order_item_key": df["order_id"] + "-" + df["order_item_id"].astype(str),
        "order_id": df["order_id"],
        "customer_key": df["customer_id"],
        "product_key": df["product_id"],
        "seller_key": df["seller_id"],
        "review_key": df["review_id"],
        "order_purchase_date_key": df["purchase_dt"].dt.strftime("%Y%m%d").astype("Int64"),
        "order_delivered_date_key": df["delivered_dt"].dt.strftime("%Y%m%d").astype("Int64"),
        "order_status": df["order_status"],
        "is_delayed": df["is_delayed"],
        "price": price,
        "freight_value": freight,
        "total_item_value": price + freight,
        "delivery_days_actual": df["delivery_days_actual"],
        "delivery_days_estimated": df["delivery_days_estimated"]
    })

    # Đảm bảo không trùng lặp khóa chính order_item_key
    fact_orders = fact_orders.drop_duplicates(subset=["order_item_key"])

    fact_orders.to_sql("fact_orders", engine, schema="gold", if_exists="append", index=False)
    print("   -> Loaded gold.fact_orders")

def run_silver_to_gold():
    """Hàm điều phối toàn bộ quá trình Silver -> Gold"""
    engine = get_db_engine()
    
    try:
        print("=== BẮT ĐẦU CHẠY TẦNG SILVER -> GOLD ===")
        
        # 1. Tạo schema gold nếu chưa có
        create_gold_schema(engine)
        
        # 2. Truncate các bảng Gold cũ nếu đã tồn tại
        try:
            clear_existing_gold_tables(engine)
        except Exception as e:
            print(f"ℹBỏ qua TRUNCATE (có thể các bảng chưa được tạo): {e}")

        # 3. Đọc dữ liệu từ Schema Silver
        silver_data = load_silver_data(engine)
        
        # 4. Transform & Load
        transform_and_load_dims(silver_data, engine)
        transform_and_load_facts(silver_data, engine)
        
        print("\n✅TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC LOAD THÀNH CÔNG VÀO SCHEMA GOLD!")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình Silver -> Gold: {e}")

if __name__ == "__main__":
    run_silver_to_gold()