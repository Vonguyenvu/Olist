.PHONY: help init bronze silver gold run-all
# Chỉ load .env nếu biến POSTGRES_HOST chưa được set từ môi trường ngoài
# (khi chạy trong Docker, docker-compose đã set sẵn -> không bị .env đè lại)
ifndef POSTGRES_HOST
-include .env
export
endif

help:
	@echo "Các lệnh có sẵn:"
	@echo "  make init      - Tạo DDL các bảng Bronze, Silver, Gold"
	@echo "  make bronze    - Nạp dữ liệu CSV vào tầng Bronze"
	@echo "  make silver    - Chuyển đổi Bronze sang Silver"
	@echo "  make gold      - Biến đổi Silver sang Gold"
	@echo "  make run-all   - Chạy toàn bộ pipeline (init -> bronze -> silver -> gold)"

init:
	@echo "=== 1. Khởi tạo DDL bảng (BRONZE, SILVER, GOLD) ==="
	PGPASSWORD=$(POSTGRES_PASSWORD) psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -v ON_ERROR_STOP=1 -f sql/create_bronze_tables.sql
	PGPASSWORD=$(POSTGRES_PASSWORD) psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -v ON_ERROR_STOP=1 -f sql/create_silver_tables.sql
	PGPASSWORD=$(POSTGRES_PASSWORD) psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -v ON_ERROR_STOP=1 -f sql/create_gold_tables.sql

bronze:
	@echo "=== 2. Nạp dữ liệu vào Bronze ==="
	python3 -m src.load_to_bronze

silver:
	@echo "=== 3. Chuyển đổi Bronze -> Silver ==="
	python3 -m src.bronze_to_silver

gold:
	@echo "=== 4. Biến đổi Silver -> Gold ==="
	python3 -m src.silver_to_gold

run-all: init bronze silver gold
	@echo "=== Hoàn thành toàn bộ pipeline ETL ==="