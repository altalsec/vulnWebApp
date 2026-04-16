-- ============================================================
-- SOC DEMO — MySQL Setup Script
-- Run this ONCE to initialize the database
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS soc_demo;
USE soc_demo;

-- Drop and recreate users table
DROP TABLE IF EXISTS users;

-- ⚠ VULNERABILITY: Passwords stored in plaintext (no hashing)
CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64)  NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    role     VARCHAR(32)  NOT NULL DEFAULT 'analyst',
    email    VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed demo users (plaintext passwords — intentionally insecure)
INSERT INTO users (username, password, role, email) VALUES
('admin',      'admin123',    'admin',    'admin@nexus-soc.local'),
('analyst',    'analyst456',  'analyst',  'analyst@nexus-soc.local'),
('jsmith',     'password1',   'analyst',  'jsmith@nexus-soc.local'),
('mwilliams',  'sec0ps!',     'senior',   'mwilliams@nexus-soc.local');

-- Optional: alerts table for future extension
CREATE TABLE IF NOT EXISTS alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    severity    ENUM('critical','high','medium','low','info') NOT NULL,
    type        VARCHAR(128),
    src_ip      VARCHAR(45),
    dst_ip      VARCHAR(45),
    description TEXT,
    status      ENUM('new','triaging','assigned','closed') DEFAULT 'new',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Verify
SELECT id, username, role FROM users;
