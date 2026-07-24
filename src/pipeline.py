from load_to_bronze import load_csv_to_bronze
from bronze_to_silver import run_bronze_to_silver
from silver_to_gold import run_silver_to_gold

def main():
    print("🏁 BẮT ĐẦU CHẠY PIPELINE ETL OLIST MEDALLION ARCHITECTURE\n")
    
    # Bước 1: CSV -> bronze schema
    load_csv_to_bronze()
    
    # Bước 2: bronze schema -> silver schema (Cleaning)
    run_bronze_to_silver()
    
    # Bước 3: silver schema -> analytics schema (Gold - Star Schema)
    run_silver_to_gold()
    
    print("🏆 TOÀN BỘ PIPELINE ĐÃ CHẠY THÀNH CÔNG VỚI ĐẦY ĐỦ 3 TẦNG BRONZE - SILVER - GOLD!")

if __name__ == "__main__":
    main()