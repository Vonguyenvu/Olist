import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv

from logging_setup import setup_logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Đọc các biến môi trường từ file .env ở thư mục gốc dự án
load_dotenv(PROJECT_ROOT / ".env")
logger = logging.getLogger(__name__)

# Cấu hình thông số kết nối PostgreSQL
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT_RAW = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

if not DB_USER or not DB_PASSWORD or not DB_NAME:
    raise ValueError(
        "Thiếu biến môi trường PostgreSQL. Cần có POSTGRES_USER, POSTGRES_PASSWORD và POSTGRES_DB."
    )

try:
    DB_PORT = int(DB_PORT_RAW)
except (TypeError, ValueError):
    raise ValueError(
        f"POSTGRES_PORT không hợp lệ: {DB_PORT_RAW!r}. Hãy đặt một số nguyên, ví dụ 5432."
    ) from None

# URL kết nối với database
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

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
            logger.info("Kết nối thành công tới PostgreSQL database '%s' tại %s:%s", DB_NAME, DB_HOST, DB_PORT)
    except Exception:
        logger.exception("Kết nối PostgreSQL thất bại tại %s:%s", DB_HOST, DB_PORT)
        raise
        
        
if __name__ == "__main__":
    setup_logging()
    test_connection()
