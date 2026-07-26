import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Đọc các biến môi trường từ file .env (nếu có)
load_dotenv()

# Cấu hình thông số kết nối PostgreSQL
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# Tạo chuỗi kết nối với database 
DATABASE_URL = F"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 

# Khởi tạo Engine kết nối
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