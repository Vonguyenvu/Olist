import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Đọc các biến môi trường từ file .env (nếu có)
load_dotenv()

def _get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Thiếu biến môi trường bắt buộc: {var_name}")
    return value


# 1. Cấu hình thông số kết nối PostgreSQL
DB_USER = _get_required_env("POSTGRES_USER")
DB_PASSWORD = _get_required_env("POSTGRES_PASSWORD")
DB_HOST = _get_required_env("POSTGRES_HOST")
DB_PORT = _get_required_env("POSTGRES_PORT")
DB_NAME = _get_required_env("POSTGRES_DB")

# Tạo chuỗi kết nối với database 
DATABASE_URL = F"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 

# 2. Khởi tạo Engine kết nối (kèm cấu hình Connection Pool)
engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Số lượng kết nối duy trì tối đa trong pool
    max_overflow=20,       # Số kết nối vượt mức cho phép khi tải cao
    echo=False             # Đổi thành True nếu muốn log toàn bộ câu lệnh SQL ra terminal
)

def get_db_engine() -> Engine:
    """Hàm trả về Database Engine cho SQLAlchemy"""
    return engine

def test_connection():
    """Hàm kiểm tra kết nối tới Database"""
    try:
        with engine.connect() as connection:
            print(f"Kết nối thành công tới PostgreSQL Database: '{DB_NAME}' tại {DB_HOST}:{DB_PORT}")
    except Exception as e:
        print(f"Kết nối thất bại: {e}")
        
        
if __name__ == "__main__":
    test_connection()