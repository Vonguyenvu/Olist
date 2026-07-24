PROJECT_NAME/
├── dags/                         # Nơi chứa các DAGs tự động hóa bằng Airflow
│   └── olist_medallion_pipeline.py # DAG điều phối toàn bộ luồng Bronze -> Silver -> Gold
│
├── data/                         # Nơi lưu trữ dữ liệu local (nếu xử lý file)
│   ├── raw/                      # Chứa file CSV gốc tải về từ Kaggle/Olist
│   ├── bronze/                   # (Tùy chọn) Chứa dữ liệu thô dạng Parquet/CSV
│   ├── silver/                   # (Tùy chọn) Chứa dữ liệu đã làm sạch
│   └── gold/                     # (Tùy chọn) Chứa dữ liệu aggregated
│
├── sql/                          # Nơi tập trung toàn bộ mã SQL xử lý dữ liệu
│   ├── 00_ddl/                   # Khởi tạo bảng, Schema
│   │   ├── create_bronze_tables.sql
│   │   ├── create_silver_tables.sql
│   │   └── create_gold_tables.sql
│   ├── 01_bronze/                # Script nạp dữ liệu thô từ raw vào Bronze
│   │   └── load_raw_to_bronze.sql
│   ├── 02_silver/                # Script làm sạch, chuẩn hóa từ Bronze -> Silver
│   │   ├── transform_customers.sql
│   │   ├── transform_orders.sql
│   │   ├── transform_products.sql
│   │   └── transform_reviews.sql
│   └── 03_gold/                  # Script tính toán, tổng hợp từ Silver -> Gold
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       ├── fact_orders.sql
│       └── rfm_segmentation.sql  # Bảng phân tích RFM khách hàng
│
├── src/                          # Chứa mã nguồn Python phụ trợ (helper scripts)
│   ├── __init__.py
│   ├── db_connection.py         # Hàm kết nối PostgreSQL/Database
│   └── utils.py                 # Các hàm xử lý chung (Log, làm sạch chuỗi...)
│
├── docker-compose.yml            # Cấu hình chạy PostgreSQL, Airflow qua Docker
├── requirements.txt              # Các thư viện Python cần dùng (psycopg2, pandas...)
├── olist.png                     # Sơ đồ ERD
└── README.md                     # Tài liệu hướng dẫn chạy dự án