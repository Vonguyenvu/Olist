import logging

from logging_setup import setup_logging
from load_to_bronze import load_csv_to_bronze
from bronze_to_silver import run_bronze_to_silver
from silver_to_gold import run_silver_to_gold


logger = logging.getLogger(__name__)


def main():
    setup_logging()
    logger.info("Bắt đầu pipeline ETL Olist: Bronze -> Silver -> Gold")
    try:
        logger.info("Bước 1/3: CSV -> bronze")
        load_csv_to_bronze()
        logger.info("Bước 2/3: bronze -> silver")
        run_bronze_to_silver()
        logger.info("Bước 3/3: silver -> gold")
        run_silver_to_gold()
        logger.info("Pipeline ETL hoàn tất thành công")
    except Exception:
        logger.exception("Pipeline ETL thất bại")
        raise

if __name__ == "__main__":
    main()
