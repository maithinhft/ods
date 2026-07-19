-- postgresql

CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name VARCHAR(255),
    product_price DOUBLE PRECISION,
    source_updated_at BIGINT 
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    customer_city VARCHAR(100),
    customer_state VARCHAR(100),
    source_updated_at BIGINT 
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id INT PRIMARY KEY,
    seller_city VARCHAR(100),
    seller_state VARCHAR(100),
    source_updated_at BIGINT 
);

CREATE TABLE IF NOT EXISTS geolocation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(100),
    source_updated_at BIGINT 
);

ALTER TABLE sellers REPLICA IDENTITY FULL;
ALTER TABLE products REPLICA IDENTITY FULL;
ALTER TABLE customers REPLICA IDENTITY FULL;
ALTER TABLE geolocation REPLICA IDENTITY FULL;

CREATE OR REPLACE FUNCTION update_pg_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.source_updated_at = (EXTRACT(EPOCH FROM clock_timestamp()) * 1000)::BIGINT;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at BEFORE INSERT OR UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE update_pg_updated_at_column();

DROP TRIGGER IF EXISTS trg_customers_updated_at ON customers;
CREATE TRIGGER trg_customers_updated_at BEFORE INSERT OR UPDATE ON customers FOR EACH ROW EXECUTE PROCEDURE update_pg_updated_at_column();

DROP TRIGGER IF EXISTS trg_sellers_updated_at ON sellers;
CREATE TRIGGER trg_sellers_updated_at BEFORE INSERT OR UPDATE ON sellers FOR EACH ROW EXECUTE PROCEDURE update_pg_updated_at_column();

DROP TRIGGER IF EXISTS trg_geolocation_updated_at ON geolocation;
CREATE TRIGGER trg_geolocation_updated_at BEFORE INSERT OR UPDATE ON geolocation FOR EACH ROW EXECUTE PROCEDURE update_pg_updated_at_column();

\copy products(product_id, product_category_name, product_name,product_price ) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/products.csv' DELIMITER ',' CSV HEADER;

\copy geolocation(geolocation_city, geolocation_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/geolocation.csv' DELIMITER ',' CSV HEADER;

\copy customers(customer_id, customer_city, customer_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/customers.csv' DELIMITER ',' CSV HEADER;

\copy sellers(seller_id, seller_city, seller_state) FROM '/home/maithinh/Documents/big_data/vdt/project/data-generator/prepared_data/sellers.csv' DELIMITER ',' CSV HEADER;

TRUNCATE TABLE
    products,
    customers,
    sellers,
    geolocation
RESTART IDENTITY
CASCADE;

DROP TABLE
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

-- mysql

CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_status VARCHAR(50),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    source_updated_at BIGINT 
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id VARCHAR(36) NOT NULL,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    shipping_limit_date DATE,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    source_updated_at BIGINT, 

    PRIMARY KEY (order_item_id),
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS order_payments (
    order_id INT NOT NULL,
    payment_type VARCHAR(50),
    payment_value DECIMAL(10,2),
    source_updated_at BIGINT, 

    PRIMARY KEY (order_id),
    CONSTRAINT fk_order_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS stg_orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_status VARCHAR(50),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    source_updated_at BIGINT 
);

CREATE TABLE IF NOT EXISTS order_reviews (
    review_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    source_updated_at BIGINT
);

DELIMITER //

CREATE TRIGGER trg_orders_updated_at BEFORE INSERT ON orders FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//
CREATE TRIGGER trg_orders_updated_at_update BEFORE UPDATE ON orders FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//

CREATE TRIGGER trg_order_items_updated_at BEFORE INSERT ON order_items FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//
CREATE TRIGGER trg_order_items_updated_at_update BEFORE UPDATE ON order_items FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//

CREATE TRIGGER trg_order_payments_updated_at BEFORE INSERT ON order_payments FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//
CREATE TRIGGER trg_order_payments_updated_at_update BEFORE UPDATE ON order_payments FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//

CREATE TRIGGER trg_stg_orders_updated_at BEFORE INSERT ON stg_orders FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//
CREATE TRIGGER trg_stg_orders_updated_at_update BEFORE UPDATE ON stg_orders FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//

CREATE TRIGGER trg_order_reviews_updated_at BEFORE INSERT ON order_reviews FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//
CREATE TRIGGER trg_order_reviews_updated_at_update BEFORE UPDATE ON order_reviews FOR EACH ROW SET NEW.source_updated_at = ROUND(UNIX_TIMESTAMP(NOW(3)) * 1000);//

DELIMITER ;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE order_reviews;
TRUNCATE TABLE order_payments;
TRUNCATE TABLE order_items;
TRUNCATE TABLE stg_orders;
TRUNCATE TABLE orders;

SET FOREIGN_KEY_CHECKS = 1;