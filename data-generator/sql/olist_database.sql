CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name VARCHAR(255),
    product_price DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    customer_city VARCHAR(100),
    customer_state VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id INT PRIMARY KEY,
    seller_city VARCHAR(100),
    seller_state VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS geolocation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id UUID NOT NULL,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    shipping_limit_date DATE,
    price NUMERIC(10,2),
    freight_value NUMERIC(10,2),

    PRIMARY KEY (order_id, product_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_order_items_seller
        FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id)
);

CREATE TABLE IF NOT EXISTS order_payments (
    order_id INT NOT NULL,
    payment_type VARCHAR(50),
    payment_value NUMERIC(10,2),

    PRIMARY KEY (order_id),

    CONSTRAINT fk_order_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS order_reviews (
    review_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,

    CONSTRAINT fk_order_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS stg_orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

\copy products(product_id, product_category_name, product_name,product_price ) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/products.csv' DELIMITER ',' CSV HEADER;

\copy geolocation(geolocation_city, geolocation_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/geolocation.csv' DELIMITER ',' CSV HEADER;

\copy customers(customer_id, customer_city, customer_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/customers.csv' DELIMITER ',' CSV HEADER;

\copy sellers(seller_id, seller_city, seller_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/sellers.csv' DELIMITER ',' CSV HEADER;


-- xóa sạch tất cả các bảng

TRUNCATE TABLE
    order_reviews,
    order_payments,
    order_items,
    orders,
    stg_orders,
    products,
    customers,
    sellers,
    geolocation
RESTART IDENTITY
CASCADE;

DROP TABLE
    order_reviews,
    order_payments,
    order_items,
    orders,
	stg_orders,
    products,
    customers,
    sellers,
    geolocation
CASCADE;

SELECT 
    slot_name,
    plugin,
    active,
    confirmed_flush_lsn AS flink_confirmed_lsn,
    pg_current_wal_lsn() AS postgres_current_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag_size_pretty
FROM pg_replication_slots
WHERE slot_name = 'flink_slot';

SELECT pg_drop_replication_slot('flink_slot');