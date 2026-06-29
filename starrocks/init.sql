CREATE TABLE IF NOT EXISTS customers (
    customer_id INT,
    customer_state VARCHAR(100),
    customer_city VARCHAR(100),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT,
    INDEX idx_state (customer_state) USING BITMAP,
    INDEX idx_city (customer_city) USING BITMAP
) ENGINE=OLAP
PRIMARY KEY(customer_id)
DISTRIBUTED BY HASH(customer_id)
ORDER BY (customer_state, customer_city, customer_id);

CREATE TABLE IF NOT EXISTS geolocation (
    id VARCHAR(36),
    geolocation_state VARCHAR(100),
    geolocation_city VARCHAR(100),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT,
    INDEX idx_geo_state (geolocation_state) USING BITMAP
) ENGINE=OLAP
PRIMARY KEY(id)
DISTRIBUTED BY HASH(id)
ORDER BY (geolocation_state, geolocation_city, id);

CREATE TABLE IF NOT EXISTS products (
    product_id INT,
    product_category_name VARCHAR(100),
    product_name VARCHAR(255),
    product_price DECIMAL(10,2),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT
) ENGINE=OLAP
PRIMARY KEY(product_id)
DISTRIBUTED BY HASH(product_id);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id INT,
    seller_state VARCHAR(100),
    seller_city VARCHAR(100),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT
) ENGINE=OLAP
PRIMARY KEY(seller_id)
DISTRIBUTED BY HASH(seller_id);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT,
    order_purchase_timestamp DATETIME,
    order_status VARCHAR(50),
    customer_id INT,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT,
    INDEX idx_status (order_status) USING BITMAP
) ENGINE=OLAP
PRIMARY KEY(order_id, order_purchase_timestamp)
PARTITION BY date_trunc('day', order_purchase_timestamp)
DISTRIBUTED BY HASH(order_id)
ORDER BY (order_purchase_timestamp, order_status, order_id);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INT,
    product_id INT,
    order_item_id VARCHAR(36),
    seller_id INT,
    shipping_limit_date DATE,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT
) ENGINE=OLAP
PRIMARY KEY(order_id, product_id, order_item_id)
DISTRIBUTED BY HASH(order_id)
ORDER BY (order_id, product_id);

CREATE TABLE IF NOT EXISTS order_payments (
    order_id INT,
    payment_type VARCHAR(50),
    payment_value DECIMAL(10,2),
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT
) ENGINE=OLAP
PRIMARY KEY(order_id, payment_type)
DISTRIBUTED BY HASH(order_id)
ORDER BY (order_id, payment_type);

CREATE TABLE IF NOT EXISTS order_reviews (
    review_id INT,
    review_creation_date DATETIME,
    order_id INT,
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message VARCHAR(65533),
    review_answer_timestamp DATETIME,
    source_updated_at BIGINT,
    starrocks_arrived_at BIGINT
) ENGINE=OLAP
PRIMARY KEY(review_id, review_creation_date)
PARTITION BY date_trunc('day', review_creation_date)
DISTRIBUTED BY HASH(review_id)
ORDER BY (review_creation_date, review_id);

CREATE MATERIALIZED VIEW mv_orders_latency
REFRESH ASYNC EVERY(INTERVAL 1 MINUTE)
DISTRIBUTED BY HASH(time_bucket)
ORDER BY (time_bucket)
AS
SELECT 
    date_trunc('minute', from_unixtime(starrocks_arrived_at / 1000)) AS time_bucket,
    (starrocks_arrived_at - source_updated_at) AS latency_ms
FROM orders;