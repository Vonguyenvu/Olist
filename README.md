# Olist E-commerce Data Pipeline (Medallion Architecture)

Hệ thống Data Pipeline xử lý và làm sạch dữ liệu thương mại điện tử Olist (Brazil E-commerce Dataset) được thiết kế và triển khai theo kiến trúc **Medallion (Bronze -> Silver -> Gold)**, tối ưu hóa lưu trữ và truy vấn trên **PostgreSQL**, vận hành đơn giản và hiệu quả qua **Python CLI & Makefile**.

---

## 📐 Kiến trúc Hệ thống (Medallion Architecture)

Dữ liệu được xử lý qua 3 tầng lưu trữ trong PostgreSQL (`schema bronze`, `silver`, `gold`):

1. **Bronze Layer (Raw Data):** 
   - Đổ toàn bộ dữ liệu thô từ các file CSV của Olist vào PostgreSQL bằng câu lệnh `COPY` tối ưu tốc độ cao.
   - Giữ nguyên cấu trúc nguyên bản của dữ liệu nguồn.
2. **Silver Layer (Cleansed & Conformed Data):**
   - Làm sạch khoảng trắng thừa, chuẩn hóa định dạng Text (Upper/Title case).
   - Ép kiểu dữ liệu (Numeric, Datetime), xử lý các giá trị `NULL`.
   - Khử trùng lặp dữ liệu (Deduplication) dựa trên mốc thời gian cập nhật.
3. **Gold Layer (Data Warehouse - Dimensional Modeling):**
   - Thiết kế mô hình Star Schema (Sơ đồ ngôi sao) phục vụ phân tích BI và Báo cáo.
   - **Fact Tables:** `fact_orders`, `fact_payments`.
   - **Dimension Tables:** `dim_customers`, `dim_products`, `dim_sellers`, `dim_reviews`, `dim_payment_types`, `dim_date`.

---

## 🛠️ Công nghệ Sử dụng (Tech Stack)

- **Ngôn ngữ lập trình:** Python 3.10+
- **Thư viện xử lý & Kết nối DB:** Pandas, SQLAlchemy, Psycopg2
- **Cơ sở dữ liệu:** PostgreSQL 15+
- **Điều phối & Tự động hóa:** Makefile
- **Báo cáo & Trực quan hóa:** Power BI / Metabase

---

## 📂 Cấu trúc Dự án

```text
.
├── data/
│   └── bronze/                  # Chứa các file CSV nguồn của Olist
├── sql/
│   ├── create_bronze_tables.sql # DDL tạo schema & bảng tầng Bronze
│   ├── create_silver_tables.sql # DDL tạo schema & bảng tầng Silver
│   └── create_gold_tables.sql   # DDL tạo schema & bảng tầng Gold
├── src/
│   ├── db_connection.py         # Quản lý kết nối PostgreSQL bằng SQLAlchemy
│   ├── load_to_bronze.py        # Pipeline nạp CSV -> Bronze (COPY expert)
│   ├── bronze_to_silver.py      # Pipeline làm sạch Bronze -> Silver
│   └── silver_to_gold.py        # Pipeline biến đổi Silver -> Gold (Star Schema)
├── .env                         # Khai báo biến môi trường (Postgres Credentials)
├── .gitignore                   # Cấu hình bỏ qua các file rác, venv, credentials
├── Makefile                     # File điều khiển chính để vận hành pipeline
├── requirements.txt             # Các thư viện Python cần thiết
└── README.md                    # Tài liệu hướng dẫn dự án