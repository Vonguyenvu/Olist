import os
from sqlalchemy import text
from db_connection import get_db_engine

DATA_BRONZE_PATH = "data/bronze"


def create_bronze_schema(engine):
    """Đảm bảo schema bronze đã được khởi tạo trong PostgreSQL"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
        conn.commit()
    print("✅ Đã kiểm tra/khởi tạo schema 'bronze'.")


def clear_existing_bronze_tables(cursor, files_to_load):
    """Xóa dữ liệu cũ trong schema bronze trước khi nạp mới."""
    print("Đang làm sạch dữ liệu cũ trong schema bronze...")

    for table_name in files_to_load.values():
        try:
            cursor.execute(f"TRUNCATE TABLE bronze.{table_name};")
        except Exception as exc:
            print(f"ℹBỏ qua TRUNCATE bronze.{table_name} (có thể bảng chưa được tạo): {exc}")

    print("   ✅ Đã làm sạch dữ liệu cũ trong schema bronze.\n")

def load_csv_to_bronze():
    engine = get_db_engine()
    create_bronze_schema(engine)
    
    files_to_load = {
        "olist_customers_dataset.csv": "customers",
        "olist_orders_dataset.csv": "orders",
        "olist_order_items_dataset.csv": "order_items",
        "olist_order_payments_dataset.csv": "order_payments",
        "olist_order_reviews_dataset.csv": "order_reviews",
        "olist_products_dataset.csv": "products",
        "olist_sellers_dataset.csv": "sellers",
        "product_category_name_translation.csv": "product_category_name_translation",
        "olist_geolocation_dataset.csv": "geolocation"
    }

    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()

    try:
        print("\n === CHẠY LOAD BRONZE BẰNG PSYCOPG2 COPY_EXPERT ===")
        clear_existing_bronze_tables(cursor, files_to_load)
        
        for file_name, table_name in files_to_load.items():
            file_path = os.path.abspath(os.path.join(DATA_BRONZE_PATH, file_name))
            
            if not os.path.exists(file_path):
                print(f"⚠️ Không tìm thấy file: {file_path}, bỏ qua...")
                continue
            
            # 2. Xử lý COPY
            if table_name == "order_reviews":
                # Đổi ESCAPE thành '"' để xử lý chuẩn các dấu " bên trong đoạn văn comment
                copy_sql = f"""
                    COPY bronze.{table_name}
                    FROM STDIN
                    WITH (
                        FORMAT csv,
                        HEADER true,
                        DELIMITER ',',
                        QUOTE '"',
                        ESCAPE '"'
                    );
                """
            else:
                copy_sql = f"""
                    COPY bronze.{table_name}
                    FROM STDIN
                    WITH (
                        FORMAT csv,
                        HEADER true,
                        DELIMITER ','
                    );
                """
            
            with open(file_path, 'r', encoding='utf-8') as f:
                cursor.copy_expert(sql=copy_sql, file=f)
                
            print(f"   -> Đã COPY thành công bronze.{table_name}")
            
        raw_conn.commit()
        print("\n ✅ HOÀN THÀNH LOAD TẤT CẢ FILE VÀO SCHEMA BRONZE!\n")
        
    except Exception as e:
        raw_conn.rollback()
        print(f"❌ Lỗi trong quá trình COPY: {e}")
    finally:
        cursor.close()
        raw_conn.close()

if __name__ == "__main__":
    load_csv_to_bronze()