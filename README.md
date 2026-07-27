# 🛒 Olist E-commerce Data Pipeline (Medallion Architecture)

Hệ thống Data Pipeline xử lý, làm sạch và mô hình hóa dữ liệu Thương mại điện tử Olist (Brazil) theo chuẩn kiến trúc **Medallion (Bronze ➔ Silver ➔ Gold)**. Dự án sử dụng **PostgreSQL** làm Data Warehouse, **Python CLI** xử lý logic và **Makefile** điều khiển luồng tự động.

---

## Kiến trúc Dữ liệu (Medallion Architecture)

Dữ liệu được tổ chức và biến đổi qua 3 Schemas riêng biệt trong PostgreSQL:

1. **Bronze Layer (Raw Data):**
   - Nạp dữ liệu thô từ các file CSV gốc vào các bảng `bronze.*`.
   - Giữ nguyên định dạng và cấu trúc dữ liệu ban đầu.

2. **Silver Layer (Cleansed & Conformed):**
   - Làm sạch dữ liệu: Chuẩn hóa chuỗi (strip/case), ép kiểu dữ liệu (Timestamp, Numeric), xử lý giá trị `NULL`.
   - Khử trùng lặp (Deduplication) dựa trên mốc thời gian.

3. **Gold Layer (Data Warehouse - Star Schema):**
   - Biến đổi dữ liệu sang mô hình hằng số & sự kiện phục vụ phân tích BI.
   - **Fact Tables:** `fact_orders`, `fact_payments`.
   - **Dimension Tables:** `dim_customers`, `dim_products`, `dim_sellers`, `dim_reviews`, `dim_payment_types`, `dim_date`.

---

## 🛠️ Công nghệ Sử dụng (Tech Stack)

- **Ngôn ngữ:** Python 3.10+
- **Thư viện xử lý:** Pandas, SQLAlchemy, Psycopg2
- **Cơ sở dữ liệu:** PostgreSQL 15+
- **Công cụ điều khiển:** Make (Linux CLI)
- **Báo cáo & BI:** Power BI

---

## 📁 Cấu trúc Thư mục Dự án

```text
Olist/
├── sql/
│   ├── create_bronze_tables.sql # DDL tạo bảng tầng Bronze (IF NOT EXISTS)
│   ├── create_silver_tables.sql # DDL tạo bảng tầng Silver
│   └── create_gold_tables.sql   # DDL tạo bảng tầng Gold
├── src/
│   ├── db_connection.py         # Cấu hình kết nối PostgreSQL
│   ├── load_to_bronze.py        # Pipeline nạp CSV -> Bronze
│   ├── bronze_to_silver.py      # Pipeline làm sạch Bronze -> Silver
│   └── silver_to_gold.py        # Pipeline mô hình hóa Silver -> Gold
├── .env                         # Khai báo biến môi trường (Credentials)
├── .gitignore                   # Bỏ qua venv, .env, cache
├── Makefile                     # Điều khiển và tự động hóa Pipeline
├── requirements.txt             # Danh sách các thư viện Python
└── README.md                    # Tài liệu hướng dẫn dự án
