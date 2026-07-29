CREATE SCHEMA IF NOT EXISTS bronze;

DROP TABLE IF EXISTS bronze.customers CASCADE;
CREATE TABLE bronze.customers(
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

DROP TABLE IF EXISTS bronze.orders CASCADE;
CREATE TABLE bronze.orders(
    order_id TEXT,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    order_approved_at TEXT,
    order_delivered_carrier_date TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT
);

DROP TABLE IF EXISTS bronze.order_items CASCADE;
CREATE TABLE bronze.order_items (
    order_id TEXT,
    order_item_id TEXT,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TEXT,
    price TEXT,
    freight_value TEXT
);

DROP TABLE IF EXISTS bronze.order_payments CASCADE;
CREATE TABLE bronze.order_payments (
    order_id TEXT,
    payment_sequential TEXT,
    payment_type TEXT,
    payment_installments TEXT,
    payment_value TEXT
);

DROP TABLE IF EXISTS bronze.order_reviews CASCADE;
CREATE TABLE bronze.order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score TEXT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TEXT,
    review_answer_timestamp TEXT
);

DROP TABLE IF EXISTS bronze.products CASCADE;
CREATE TABLE bronze.products (
    product_id TEXT,
    product_category_name TEXT,
    product_name_lenght TEXT,
    product_description_lenght TEXT,
    product_photos_qty TEXT,
    product_weight_g TEXT,
    product_length_cm TEXT,
    product_height_cm TEXT,
    product_width_cm TEXT
);

DROP TABLE IF EXISTS bronze.sellers CASCADE;
CREATE TABLE bronze.sellers (
    seller_id TEXT,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

DROP TABLE IF EXISTS bronze.product_category_name_translation CASCADE;
CREATE TABLE bronze.product_category_name_translation (
    product_category_name TEXT,
    product_category_name_english TEXT
);

DROP TABLE IF EXISTS bronze.geolocation CASCADE;
CREATE TABLE bronze.geolocation (
    geolocation_zip_code_prefix TEXT,
    geolocation_lat TEXT,
    geolocation_lng TEXT,
    geolocation_city TEXT,
    geolocation_state TEXT
);