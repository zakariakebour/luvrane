CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 35e5cfd1b16d

CREATE TABLE cart_items (
    id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36) NOT NULL, 
    product_id VARCHAR(36) NOT NULL, 
    variant_id VARCHAR(36), 
    quantity INTEGER, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE order_items (
    id VARCHAR(36) NOT NULL, 
    order_id VARCHAR(36) NOT NULL, 
    product_id VARCHAR(36) NOT NULL, 
    variant_id VARCHAR(36), 
    quantity INTEGER NOT NULL, 
    unit_price NUMERIC(10, 2) NOT NULL, 
    total_price NUMERIC(10, 2) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE orders (
    id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36) NOT NULL, 
    address_id VARCHAR(36) NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    total_price NUMERIC(10, 2) NOT NULL, 
    notes VARCHAR(500), 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    delivered_at TIMESTAMP WITHOUT TIME ZONE, 
    cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE product_images (
    id VARCHAR(36) NOT NULL, 
    image_url VARCHAR(255) NOT NULL, 
    media_type VARCHAR(255), 
    position INTEGER, 
    product_id VARCHAR(36) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE product_likes (
    id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36) NOT NULL, 
    product_id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE product_option_values (
    id VARCHAR(36) NOT NULL, 
    option_id VARCHAR(36) NOT NULL, 
    value VARCHAR(50) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE product_options (
    id VARCHAR(36) NOT NULL, 
    product_id VARCHAR(36) NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE product_variants (
    id VARCHAR(36) NOT NULL, 
    stock INTEGER, 
    price NUMERIC(10, 2), 
    sku VARCHAR(100) NOT NULL, 
    signature VARCHAR(255) NOT NULL, 
    product_id VARCHAR(36) NOT NULL, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE products (
    id VARCHAR(36) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    price NUMERIC(10, 2) NOT NULL, 
    store_id VARCHAR(36) NOT NULL, 
    is_active BOOLEAN, 
    deleted_at TIMESTAMP WITHOUT TIME ZONE, 
    status VARCHAR(30) NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE stores (
    id VARCHAR(36) NOT NULL, 
    owner_id VARCHAR(36) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    type VARCHAR(100) NOT NULL, 
    photo_profile VARCHAR(255), 
    image VARCHAR(255), 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    deleted_at TIMESTAMP WITHOUT TIME ZONE, 
    is_active BOOLEAN, 
    PRIMARY KEY (id)
);

CREATE TABLE user_addresses (
    id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36) NOT NULL, 
    street VARCHAR(255) NOT NULL, 
    city VARCHAR(100) NOT NULL, 
    wilaya VARCHAR(100) NOT NULL, 
    postal_code VARCHAR(20), 
    is_default BOOLEAN, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id VARCHAR(36) NOT NULL, 
    username VARCHAR(50) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    hashed_password VARCHAR(255) NOT NULL, 
    role VARCHAR(20) NOT NULL, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    deleted_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE variant_values (
    id VARCHAR(36) NOT NULL, 
    variant_id VARCHAR(36) NOT NULL, 
    option_value_id VARCHAR(36) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (variant_id, option_value_id)
);

INSERT INTO alembic_version (version_num) VALUES ('35e5cfd1b16d');
