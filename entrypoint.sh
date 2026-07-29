#!/bin/sh
# entrypoint.sh — thay thế Makefile, chạy toàn bộ pipeline ETL theo thứ tự
# init (DDL) -> bronze -> silver -> gold
set -e  # dừng ngay nếu bất kỳ bước nào lỗi

run_sql() {
  echo "-> $1"
  PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v ON_ERROR_STOP=1 \
    -f "$1"
}

echo "=== 1. Khởi tạo DDL bảng (BRONZE, SILVER, GOLD) ==="
run_sql sql/create_bronze_tables.sql
run_sql sql/create_silver_tables.sql
run_sql sql/create_gold_tables.sql

echo "=== 2. Chạy tầng BRONZE ==="
python3 -m src.load_to_bronze

echo "=== 3. Chạy tầng SILVER ==="
python3 -m src.bronze_to_silver

echo "=== 4. Chạy tầng GOLD ==="
python3 -m src.silver_to_gold

echo "=== Hoàn thành toàn bộ pipeline ETL ==="