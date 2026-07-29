# Olist E-commerce Data Pipeline

Hệ thống Data Pipeline xử lý, làm sạch và mô hình hóa dữ liệu Thương mại điện tử Olist (Brazil) theo chuẩn kiến trúc **Medallion (Bronze ➔ Silver ➔ Gold)**. Dự án sử dụng **PostgreSQL** làm Data Warehouse, **Python CLI** xử lý logic và **Makefile** điều khiển luồng tự động.

![Mô tả dataset Olist](images/olist.png)

---

## Kiến trúc Dữ liệu (Medallion Architecture)

Dữ liệu được tổ chức và biến đổi qua 3 Schemas riêng biệt trong PostgreSQL:

1. **Bronze Layer (Raw Data):**
   - Nạp dữ liệu thô từ các file CSV gốc vào các bảng `bronze.*`.
   - Giữ nguyên định dạng và cấu trúc dữ liệu ban đầu.

2. **Silver Layer (Cleansed & Conformed):**
   - Làm sạch dữ liệu: Chuẩn hóa chuỗi (strip/case), ép kiểu dữ liệu (Timestamp, Numeric), xử lý giá trị `NULL`.
   - Khử trùng lặp dựa trên mốc thời gian.

3. **Gold Layer (Data Warehouse - Star Schema):**
   - Biến đổi dữ liệu sang mô hình hằng số & sự kiện phục vụ phân tích BI.
   - **Fact Tables:** `fact_orders`, `fact_payments`.
   - **Dimension Tables:** `dim_customers`, `dim_products`, `dim_sellers`, `dim_reviews`, `dim_payment_types`, `dim_date`.

![Mô tả mô hình star schema với các bảng dimension và fact](images/schema.png)

---

## Công nghệ Sử dụng 

- **Ngôn ngữ:** Python 
- **Thư viện xử lý:** Pandas, SQLAlchemy, Psycopg2
- **Cơ sở dữ liệu:** PostgreSQL 
- **Công cụ điều khiển:** Make (Linux CLI)
- **Báo cáo & BI:** Power BI

---

## Vận hành
 
### 1. Tải dữ liệu Olist
 
Tải bộ dữ liệu từ Kaggle tại đường dẫn sau:
 
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
 
Sau khi tải về, đặt toàn bộ file dữ liệu vào thư mục `data/` rồi giải nén tại đó. Thư mục `data/` sẽ chứa các file CSV nguồn dùng cho pipeline.
 
### 2. Tạo file cấu hình `.env`
 
Chỉnh sửa thông tin kết nối với database ở file `.env`:
 
```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_HOST_PORT=5433
POSTGRES_DB=olist
```
 
> `POSTGRES_HOST_PORT` chỉ dùng khi chạy Docker — là cổng map ra máy host (dùng để tránh xung đột nếu máy bạn đã có PostgreSQL chạy sẵn trên `5432`). Khi chạy trong container, biến `POSTGRES_HOST` sẽ tự động được `docker-compose.yml` override thành `postgres` (tên service), giá trị `localhost` ở đây chỉ áp dụng khi bạn chạy pipeline trực tiếp trên máy (mục "Chạy không dùng Docker" bên dưới).
 
---
 
## Cách A — Chạy bằng Docker (khuyến nghị)
 
Cách nhanh nhất, không cần cài PostgreSQL hay Python venv thủ công.
 
**Build và chạy pipeline (Postgres + pipeline):**
 
```bash
docker compose up --build
```
 
**Dừng toàn bộ và xóa data:**
 
```bash
docker compose down -v
```
 
**Chỉ dừng, giữ lại data:**
 
```bash
docker compose down
```
 
Pipeline tự động chạy tuần tự init (DDL) → bronze → silver → gold khi container `pipeline` khởi động, không cần gõ thêm lệnh nào khác.
 
---
 
## Cách B — Chạy không dùng Docker
 
Dùng khi bạn muốn debug nhanh từng bước hoặc không có Docker trên máy.
 
**1. Khởi tạo môi trường ảo và cài thư viện:**
 
```bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
 
**2. Cài đặt PostgreSQL và tạo database:**
 
```sql
CREATE DATABASE olist;
```
 
**3. Chạy từng bước pipeline thủ công** (không còn `make run-all` vì Makefile đã được thay bằng Docker entrypoint):
 
```bash
# Khởi tạo DDL (Bronze, Silver, Gold)
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d olist -f sql/create_bronze_tables.sql
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d olist -f sql/create_silver_tables.sql
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d olist -f sql/create_gold_tables.sql
 
# Chạy ETL từng tầng
python3 -m src.load_to_bronze
python3 -m src.bronze_to_silver
python3 -m src.silver_to_gold
```
 
> Đảm bảo PostgreSQL đang chạy trước khi thực thi các lệnh trên.

