-- Supabase Database Setup Script
-- Run this in Supabase SQL Editor

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create deals table
CREATE TABLE IF NOT EXISTS deals (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    price REAL NOT NULL,
    original_price REAL,
    discount INTEGER,
    image_filename TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create deal_of_the_day table
CREATE TABLE IF NOT EXISTS deal_of_the_day (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO categories(name, slug) VALUES
    ('Electronics', 'electronics'),
    ('Fashion', 'fashion'),
    ('Home & Kitchen', 'home'),
    ('Beauty', 'beauty'),
    ('Books', 'books'),
    ('Sports', 'sports')
ON CONFLICT (name) DO NOTHING;

