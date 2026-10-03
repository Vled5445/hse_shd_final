DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_namespace WHERE nspname = 'student46'
    ) THEN
        EXECUTE 'CREATE SCHEMA student46 AUTHORIZATION student46';
    END IF;
END$$;

CREATE TABLE student46.h_sales (
    h_sales_hash      VARCHAR(32)   PRIMARY KEY,
    sale_id           UUID          NOT NULL,
    source_system     VARCHAR(100)  NOT NULL,
    load_dttm         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE student46.h_customer (
    h_customer_hash   VARCHAR(32)   PRIMARY KEY,
    customer_id       UUID          NOT NULL,
    source_system     VARCHAR(100)  NOT NULL,
    load_dttm         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE student46.h_product (
    h_product_hash    VARCHAR(32)   PRIMARY KEY,
    product_id        UUID          NOT NULL,
    source_system     VARCHAR(100)  NOT NULL,
    load_dttm         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE student46.h_shipment (
    h_shipment_hash   VARCHAR(32)   PRIMARY KEY,
    shipment_id       UUID          NOT NULL,
    source_system     VARCHAR(100)  NOT NULL,
    load_dttm         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE student46.l_customer_sale (
    l_customer_sale_hash   VARCHAR(32) PRIMARY KEY,
    h_customer_hash        VARCHAR(32) NOT NULL,
    h_sales_hash           VARCHAR(32) NOT NULL,
    record_source          VARCHAR(100) NOT NULL,
    load_dttm              TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_l_custsale_customer FOREIGN KEY (h_customer_hash) REFERENCES student46.h_customer(h_customer_hash),
    CONSTRAINT fk_l_custsale_sales FOREIGN KEY (h_sales_hash) REFERENCES student46.h_sales(h_sales_hash)
);

CREATE TABLE student46.l_sales_product (
    l_sales_product_hash   VARCHAR(32) PRIMARY KEY,
    h_sales_hash           VARCHAR(32) NOT NULL,
    h_product_hash         VARCHAR(32) NOT NULL,
    record_source          VARCHAR(100) NOT NULL,
    load_dttm              TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_l_salesprod_sales FOREIGN KEY (h_sales_hash) REFERENCES student46.h_sales(h_sales_hash),
    CONSTRAINT fk_l_salesprod_product FOREIGN KEY (h_product_hash) REFERENCES student46.h_product(h_product_hash)
);

CREATE TABLE student46.l_sales_shipment (
    l_sales_shipment_hash  VARCHAR(32) PRIMARY KEY,
    h_sales_hash           VARCHAR(32) NOT NULL,
    h_shipment_hash        VARCHAR(32) NOT NULL,
    record_source          VARCHAR(100) NOT NULL,
    load_dttm              TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_l_salesship_sales FOREIGN KEY (h_sales_hash) REFERENCES student46.h_sales(h_sales_hash),
    CONSTRAINT fk_l_salesship_shipment FOREIGN KEY (h_shipment_hash) REFERENCES student46.h_shipment(h_shipment_hash)
);

CREATE TABLE student46.s_customer_segment (
    h_customer_hash VARCHAR(32) NOT NULL,
    load_dttm TIMESTAMP NOT NULL,
    customer_segment TEXT,
    hash_diff TEXT,
    record_source TEXT,
    PRIMARY KEY (h_customer_hash, load_dttm),
    CONSTRAINT fk_s_customer_segment FOREIGN KEY (h_customer_hash) REFERENCES student46.h_customer(h_customer_hash)
) DISTRIBUTED REPLICATED;

CREATE TABLE student46.s_customer_address (
    h_customer_hash VARCHAR(32) NOT NULL,
    load_dttm TIMESTAMP NOT NULL,
    postal_code TEXT,
    country TEXT,
    region TEXT,
    state TEXT,
    city TEXT,
    hash_diff TEXT,
    record_source TEXT,
    PRIMARY KEY (h_customer_hash, load_dttm),
    CONSTRAINT fk_s_customer_address FOREIGN KEY (h_customer_hash) REFERENCES student46.h_customer(h_customer_hash)
) DISTRIBUTED REPLICATED;

CREATE TABLE student46.s_product_info (
    h_product_hash VARCHAR(32) NOT NULL,
    load_dttm TIMESTAMP NOT NULL,
    category TEXT,
    sub_category TEXT,
    hash_diff TEXT,
    record_source TEXT,
    PRIMARY KEY (h_product_hash, load_dttm),
    CONSTRAINT fk_s_product_info FOREIGN KEY (h_product_hash) REFERENCES student46.h_product(h_product_hash)
) DISTRIBUTED REPLICATED;

CREATE TABLE student46.s_sales_metrics (
    l_sales_product_hash VARCHAR(32) NOT NULL,
    load_dttm TIMESTAMP NOT NULL,
    quantity NUMERIC,
    sales NUMERIC,
    discount NUMERIC,
    profit NUMERIC,
    hash_diff TEXT,
    record_source TEXT,
    PRIMARY KEY (l_sales_product_hash, load_dttm)
) DISTRIBUTED REPLICATED;