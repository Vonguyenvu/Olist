# import os
# import pandas as pd
# from db_connection import get_db_engine

# DATA_BRONZE_PATH = "data/bronze"

# def load_csv_to_bronze():
#     engine = get_db_engine()
    
#     files_to_load = {
#         "olist_customers_dataset.csv": "customers",
#         "olist_orders_dataset.csv": "orders",
#         "olist_order_items_dataset.csv": "order_items",
#         "olist_order_payments_dataset.csv": "order_payments",
#         "olist_order_reviews_dataset.csv": "order_reviews",
#         "olist_products_dataset.csv": "products",
#         "olist_sellers_dataset.csv": "sellers",
#         "product_category_name_translation.csv": "product_category_name_translation",
#         "olist_geolocation_dataset.csv": "geolocation"
#     }

#     print("\n🚀 === CHẠY LOAD BRONZE BẰNG PANDAS TO_SQL ===")

#     for file_name, table_name in files_to_load.items():
#         file_path = os.path.join(DATA_BRONZE_PATH, file_name)
        
#         print(f"📥 Đang đọc {file_name}...")
        
#         # Đọc tất cả thành STRING/TEXT (chuẩn Bronze)
#         df = pd.read_csv(file_path, dtype=str)
        
#         # Nạp dữ liệu vào bảng có sẵn
#         df.to_sql(
#             name=table_name,
#             con=engine,
#             schema="bronze",
#             if_exists="append",  # Đã tạo DDL trước đó nên dùng append để chèn dữ liệu
#             index=False,
#             method="multi",      # Tối ưu chèn theo nhiều lô (batch insert)
#             chunksize=5000       # Chia lô 5000 dòng/lần
#         )
#         print(f"   ✅ Đã nạp thành công bronze.{table_name}")

#     print("\n🎉 HOÀN THÀNH LOAD SCHEMA BRONZE!\n")

# if __name__ == "__main__":
#     load_csv_to_bronze()
    
    
    
    
# import os
# from db_connection import get_db_engine

# DATA_BRONZE_PATH = "data/bronze"

# def load_bronze_with_copy_expert():
#     engine = get_db_engine()
    
#     files_to_load = {
#         "olist_customers_dataset.csv": "customers",
#         "olist_orders_dataset.csv": "orders",
#         "olist_order_items_dataset.csv": "order_items",
#         "olist_order_payments_dataset.csv": "order_payments",
#         "olist_order_reviews_dataset.csv": "order_reviews",
#         "olist_products_dataset.csv": "products",
#         "olist_sellers_dataset.csv": "sellers",
#         "product_category_name_translation.csv": "product_category_name_translation",
#         "olist_geolocation_dataset.csv": "geolocation"
#     }

#     raw_conn = engine.raw_connection()
#     cursor = raw_conn.cursor()

#     try:
#         print("\n🚀 === CHẠY LOAD BRONZE BẰNG PSYCOPG2 COPY_EXPERT ===")
        
#         for file_name, table_name in files_to_load.items():
#             file_path = os.path.abspath(os.path.join(DATA_BRONZE_PATH, file_name))
            
#             if not os.path.exists(file_path):
#                 print(f"⚠️ Không tìm thấy file: {file_path}, bỏ qua...")
#                 continue

#             # 1. Truncate dữ liệu cũ trước khi nạp
#             cursor.execute(f"TRUNCATE TABLE bronze.{table_name};")
            
#             # 2. Xử lý COPY
#             if table_name == "order_reviews":
#                 # Đổi ESCAPE thành '"' để xử lý chuẩn các dấu " bên trong đoạn văn comment
#                 copy_sql = f"""
#                     COPY bronze.{table_name}
#                     FROM STDIN
#                     WITH (
#                         FORMAT csv,
#                         HEADER true,
#                         DELIMITER ',',
#                         QUOTE '"',
#                         ESCAPE '"'
#                     );
#                 """
#             else:
#                 copy_sql = f"""
#                     COPY bronze.{table_name}
#                     FROM STDIN
#                     WITH (
#                         FORMAT csv,
#                         HEADER true,
#                         DELIMITER ','
#                     );
#                 """
            
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 cursor.copy_expert(sql=copy_sql, file=f)
                
#             print(f"   ✅ Đã COPY thành công bronze.{table_name}")
            
#         raw_conn.commit()
#         print("\n🎉 HOÀN THÀNH LOAD TẤT CẢ FILE VÀO SCHEMA BRONZE!\n")
        
#     except Exception as e:
#         raw_conn.rollback()
#         print(f"❌ Lỗi trong quá trình COPY: {e}")
#     finally:
#         cursor.close()
#         raw_conn.close()

# if __name__ == "__main__":
#     load_bronze_with_copy_expert()
    
    
    
import os
from db_connection import get_db_engine

DATA_BRONZE_PATH = "data/bronze"

def load_csv_to_bronze():
    engine = get_db_engine()
    
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
        print("\n🚀 === CHẠY LOAD BRONZE BẰNG PSYCOPG2 COPY_EXPERT ===")
        
        for file_name, table_name in files_to_load.items():
            file_path = os.path.abspath(os.path.join(DATA_BRONZE_PATH, file_name))
            
            if not os.path.exists(file_path):
                print(f"⚠️ Không tìm thấy file: {file_path}, bỏ qua...")
                continue

            # 1. Truncate dữ liệu cũ trước khi nạp
            cursor.execute(f"TRUNCATE TABLE bronze.{table_name};")
            
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
                
            print(f"   ✅ Đã COPY thành công bronze.{table_name}")
            
        raw_conn.commit()
        print("\n🎉 HOÀN THÀNH LOAD TẤT CẢ FILE VÀO SCHEMA BRONZE!\n")
        
    except Exception as e:
        raw_conn.rollback()
        print(f"❌ Lỗi trong quá trình COPY: {e}")
    finally:
        cursor.close()
        raw_conn.close()

if __name__ == "__main__":
    load_csv_to_bronze()