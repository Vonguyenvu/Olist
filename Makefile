.PHONY: help init bronze silver gold run-all

# Nạp tất cả biến từ file .env vào Makefile
-include .env
export
# Chạy make + help/init/bronze/silver/gold/run-all để chạy tự động trong 1 lần

help:
	@echo "Các lệnh hỗ trợ:"
	@echo "  make init      - Khởi tạo DDL bảng"
	@echo "  make run-all   - Chạy toàn bộ Pipeline"

init:
	@echo "=== 1. KHỞI TẠO DDL BẢNG (BRONZE, SILVER, GOLD) ==="
	@PGPASSWORD="$(POSTGRES_PASSWORD)" psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f sql/create_bronze_tables.sql
	@PGPASSWORD="$(POSTGRES_PASSWORD)" psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f sql/create_silver_tables.sql
	@PGPASSWORD="$(POSTGRES_PASSWORD)" psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f sql/create_gold_tables.sql

bronze:
	@echo "=== 2. CHẠY TẦNG BRONZE ==="
	python3 -m src.load_to_bronze

silver:
	@echo "=== 3. CHẠY TẦNG SILVER ==="
	python3 -m src.bronze_to_silver

gold:
	@echo "=== 4. CHẠY TẦNG GOLD ==="
	python3 -m src.silver_to_gold

run-all: init bronze silver gold
	@echo "=== HOÀN THÀNH TOÀN BỘ PIPELINE ETL ==="