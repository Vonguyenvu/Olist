-- Tạo schema chứa Data Warehouse
CREATE SCHEMA IF NOT EXISTS gold;

-- 1. Bảng Dim Customers 
CREATE TABLE gold.dim_customers (
    customer_key VARCHAR(50) PRIMARY KEY, 
    customer_unique_id VARCHAR(50), 
    customer_zip_code_prefix INT, 
    customer_city VARCHAR(100), 
    customer_state VARCHAR(50)
);

-- 2. Bảng Dim Products
CREATE TABLE gold.dim_products (
    product_key VARCHAR(50) PRIMARY KEY,
    product_category_name_pt VARCHAR(100),
    product_category_name_en VARCHAR(100),
    product_weight_g INT, 
    product_length_cm INT, 
    product_height_cm INT,
    product_width_cm INT
);

-- 3. Bảng Dim Sellers 
CREATE TABLE gold.dim_sellers (
    seller_key VARCHAR(50) PRIMARY KEY, 
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(5)
);

-- 4. Bảng Dim Date 
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY, 
    full_date DATE,
    year INT,
    quarter INT, 
    month INT, 
    month_name VARCHAR(20),
    day_of_week INT,
    is_weekend BOOLEAN
);

-- 5. Bảng Dim Reviews (Đã sửa lỗi typo riview -> review)
CREATE TABLE gold.dim_reviews (
    review_key VARCHAR(50) PRIMARY KEY,
    review_score INT,
    review_comment_title TEXT, 
    review_comment_message TEXT,
    review_creation_date TIMESTAMP, 
    review_answer_timestamp TIMESTAMP,
    has_comment BOOLEAN
);

-- 6. Bảng Dim Payment Types 
CREATE TABLE gold.dim_payment_types (
    payment_type_key VARCHAR(50) PRIMARY KEY,
    payment_type_name VARCHAR(30)
);

-- 7. Bảng Fact Payments 
CREATE TABLE gold.fact_payments (
    payment_id VARCHAR(100) PRIMARY KEY, -- order_id + payment_sequential
    order_id VARCHAR(50),
    customer_key VARCHAR(50) REFERENCES gold.dim_customers(customer_key),
    payment_type_key VARCHAR(50) REFERENCES gold.dim_payment_types(payment_type_key),
    payment_sequential INT,
    payment_installments INT,
    payment_value NUMERIC(10, 2)
);

-- 8. Bảng Fact Orders 
CREATE TABLE gold.fact_orders (
    -- 1. PRIMARY KEY
    order_item_key VARCHAR(100) PRIMARY KEY, -- order_id || '-' || order_item_id

    -- 2. DEGENERATE DIMENSION
    order_id VARCHAR(50) NOT NULL,

    -- 3. FOREIGN KEYS
    customer_key VARCHAR(50) REFERENCES gold.dim_customers(customer_key),
    product_key VARCHAR(50) REFERENCES gold.dim_products(product_key),
    seller_key VARCHAR(50) REFERENCES gold.dim_sellers(seller_key),
    review_key VARCHAR(50) REFERENCES gold.dim_reviews(review_key),
    
    -- Date Keys
    order_purchase_date_key INT REFERENCES gold.dim_date(date_key),
    order_delivered_date_key INT REFERENCES gold.dim_date(date_key),

    -- 4. ATTRIBUTES / FLAGS
    order_status VARCHAR(30),
    is_delayed BOOLEAN,

    -- 5. MEASURES / METRICS
    price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2),
    total_item_value NUMERIC(10, 2),
    delivery_days_actual INT,
    delivery_days_estimated INT
);