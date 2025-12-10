-- WSOPTV Test Seed Data
-- Purpose: Initialize test database with minimal required data
-- WARNING: This file is for TEST environment only!

-- Test Admin User (password: testadmin123)
-- Hash generated with bcrypt, cost=12
INSERT INTO users (username, email, hashed_password, display_name, is_admin, is_approved, created_at, updated_at)
VALUES (
    'testadmin',
    'testadmin@test.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4LmVvPvPJfXk2p1K',
    'Test Admin',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- Test Regular User (password: testuser123)
INSERT INTO users (username, email, hashed_password, display_name, is_admin, is_approved, created_at, updated_at)
VALUES (
    'testuser',
    'testuser@test.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4LmVvPvPJfXk2p1K',
    'Test User',
    false,
    true,
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- Test Catalog
INSERT INTO catalogs (id, name, display_title, description, created_at, updated_at)
VALUES (
    'test-catalog-001',
    'Test Catalog',
    'Test Catalog Title',
    'A catalog for testing purposes',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
