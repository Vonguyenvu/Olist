# Olist E-commerce Data Pipeline

Hệ thống Data Pipeline xử lý, làm sạch và mô hình hóa dữ liệu Thương mại điện tử Olist (Brazil) theo chuẩn kiến trúc **Medallion (Bronze ➔ Silver ➔ Gold)**. Dự án sử dụng **PostgreSQL** làm Data Warehouse, **Python** xử lý logic ETL, và **Docker Compose** điều phối toàn bộ pipeline chạy tự động.

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

## Orchestration bằng Airflow
 
DAG `olist_medallion_pipeline` điều phối toàn bộ pipeline theo đúng kiến trúc Medallion, chạy tuần tự 4 bước:
 
```
init_ddl → load_bronze → transform_silver → transform_gold
```
 
| Task | Nội dung |
|---|---|
| `init_ddl` | Khởi tạo DDL cho 3 schema Bronze, Silver, Gold |
| `load_bronze` | Nạp CSV nguồn vào tầng Bronze |
| `transform_silver` | Làm sạch, chuẩn hóa dữ liệu Bronze → Silver |
| `transform_gold` | Biến đổi Silver → mô hình Star Schema ở tầng Gold |
 
Mỗi task chạy tuần tự, task sau chỉ chạy khi task trước hoàn thành thành công — đảm bảo tính toàn vẹn dữ liệu qua từng tầng. Airflow cho phép theo dõi trạng thái, xem log riêng từng bước, và retry tự động khi có lỗi.

---

## Công nghệ Sử dụng 

- **Ngôn ngữ:** Python 
- **Thư viện xử lý:** Pandas, SQLAlchemy, Psycopg2
- **Cơ sở dữ liệu:** PostgreSQL 
- **Containerization & điều phối:** Docker, Docker Compose
- **Báo cáo & BI:** Power BI
- **Workflow Orchestration:** Apache Airflow

---

## Vận hành
 
### 1. Tải dữ liệu Olist
 
Tải bộ dữ liệu từ Kaggle tại đường dẫn sau:
 
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
 
Sau khi tải về, đặt toàn bộ file dữ liệu vào thư mục `data/` rồi giải nén tại đó. Thư mục `data/` sẽ chứa các file CSV nguồn dùng cho pipeline.

### 2. Cài đặt PostgreSQL và tạo database olist 
 
```sql
CREATE DATABASE olist;
```
 
### 3. Chỉnh sửa file cấu hình `.env`
 
Chỉnh sửa thông tin kết nối với database ở file `.env`:
 
```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_HOST_PORT=5433
POSTGRES_DB=olist
```

> `POSTGRES_HOST_PORT` chỉ dùng khi chạy Docker — là cổng map ra máy host (dùng để tránh xung đột nếu máy bạn đã có PostgreSQL chạy sẵn trên `5432`). Khi chạy trong container, biến `POSTGRES_HOST` sẽ tự động được `docker-compose.yml` override thành `postgres` (tên service), giá trị `localhost` ở đây chỉ áp dụng khi bạn chạy pipeline trực tiếp trên máy.
 
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
 
 
**2. Vận hành Data Pipeline bằng Makefile**
 
Sau khi đã có dữ liệu (đặt trong `data/`), môi trường ảo, và cấu hình database, chạy toàn bộ pipeline:
 
```bash
make run-all
```
 
Lệnh này lần lượt chạy:
1. `make init` — Tạo các bảng ở tầng Bronze, Silver, Gold.
2. `make bronze` — Nạp dữ liệu CSV vào Bronze.
3. `make silver` — Chuyển đổi dữ liệu Bronze sang Silver.
4. `make gold` — Biến đổi dữ liệu Silver sang Gold.

Cũng có thể chạy riêng từng bước nếu cần debug:

```bash
make init      # chỉ tạo DDL
make bronze    # chỉ nạp Bronze
make silver    # chỉ chuyển Bronze -> Silver
make gold      # chỉ biến đổi Silver -> Gold
```
 
Xem toàn bộ lệnh có sẵn:
 
```bash
make help
```
 
### Lưu ý
 
- Đảm bảo PostgreSQL đang chạy trước khi thực thi `make run-all`.
- Nếu cần tạo lại schema từ đầu, chạy riêng `make init` — DDL đã tự `DROP TABLE IF EXISTS` trước khi tạo, nên chạy lại bao nhiêu lần cũng an toàn.
 

