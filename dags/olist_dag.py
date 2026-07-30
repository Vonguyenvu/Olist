from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "admin",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# Python nằm trong virtualenv riêng (tạo lúc container start) - KHÔNG dùng chung
# môi trường Python với Airflow, tránh xung đột version SQLAlchemy/pandas.
PROJECT_PYTHON = "/opt/airflow/venv_project/bin/python"

with DAG(
    dag_id="olist_pipeline",
    description="Bronze -> Silver -> Gold pipeline cho dữ liệu Olist",
    default_args=default_args,
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["olist", "medallion"],
) as dag:

    # --- 1. Khởi tạo DDL (Bronze, Silver, Gold) ---
    init_ddl = BashOperator(
        task_id="init_ddl",
        bash_command=(
            "PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT "
            "-U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1 -f /opt/airflow/sql/create_bronze_tables.sql && "
            "PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT "
            "-U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1 -f /opt/airflow/sql/create_silver_tables.sql && "
            "PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT "
            "-U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1 -f /opt/airflow/sql/create_gold_tables.sql"
        ),
    )

    # --- 2. Bronze ---
    load_bronze = BashOperator(
        task_id="load_bronze",
        bash_command=f"cd /opt/airflow && {PROJECT_PYTHON} -m src.load_to_bronze",
    )

    # --- 3. Silver ---
    transform_silver = BashOperator(
        task_id="transform_silver",
        bash_command=f"cd /opt/airflow && {PROJECT_PYTHON} -m src.bronze_to_silver",
    )

    # --- 4. Gold ---
    transform_gold = BashOperator(
        task_id="transform_gold",
        bash_command=f"cd /opt/airflow && {PROJECT_PYTHON} -m src.silver_to_gold",
    )

    init_ddl >> load_bronze >> transform_silver >> transform_gold