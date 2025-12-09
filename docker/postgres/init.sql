-- WSOPTV Database Schema
-- PostgreSQL 16

-- ============================================================================
-- Types (Enums)
-- ============================================================================

CREATE TYPE user_role AS ENUM ('user', 'admin');
CREATE TYPE user_status AS ENUM ('pending', 'approved', 'rejected', 'suspended');
CREATE TYPE hand_grade AS ENUM ('S', 'A', 'B', 'C');
CREATE TYPE event_type AS ENUM ('play', 'pause', 'seek', 'complete', 'quality_change');

-- ============================================================================
-- Users
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    role user_role NOT NULL DEFAULT 'user',
    status user_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

-- ============================================================================
-- User Sessions
-- ============================================================================

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) NOT NULL UNIQUE,
    device_info TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);

-- ============================================================================
-- Catalogs
-- ============================================================================

CREATE TABLE catalogs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_title VARCHAR(200) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- ============================================================================
-- Series
-- ============================================================================

CREATE TABLE series (
    id SERIAL PRIMARY KEY,
    catalog_id VARCHAR(50) NOT NULL REFERENCES catalogs(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    year INTEGER NOT NULL,
    season_num INTEGER,
    description TEXT,
    thumbnail_url VARCHAR(500)
);

CREATE INDEX idx_series_catalog_id ON series(catalog_id);
CREATE INDEX idx_series_year ON series(year);

-- ============================================================================
-- Files (Media)
-- ============================================================================

CREATE TABLE files (
    id VARCHAR(100) PRIMARY KEY,
    nas_path VARCHAR(1000) NOT NULL UNIQUE,
    filename VARCHAR(500) NOT NULL,
    size_bytes BIGINT NOT NULL,
    duration_sec INTEGER NOT NULL,
    resolution VARCHAR(20),
    codec VARCHAR(50),
    fps FLOAT,
    bitrate_kbps INTEGER,
    hls_ready BOOLEAN NOT NULL DEFAULT FALSE,
    hls_path VARCHAR(500)
);

-- ============================================================================
-- Contents
-- ============================================================================

CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    file_id VARCHAR(100) REFERENCES files(id) ON DELETE SET NULL,
    episode_num INTEGER,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    duration_sec INTEGER NOT NULL DEFAULT 0,
    thumbnail_url VARCHAR(500),
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contents_series_id ON contents(series_id);
CREATE INDEX idx_contents_file_id ON contents(file_id);

-- ============================================================================
-- Players (Poker)
-- ============================================================================

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    country VARCHAR(50),
    avatar_url VARCHAR(500),
    total_hands INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_players_name ON players(name);

-- ============================================================================
-- Hands
-- ============================================================================

CREATE TABLE hands (
    id SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    file_id VARCHAR(100) REFERENCES files(id) ON DELETE SET NULL,
    hand_number INTEGER,
    start_sec INTEGER NOT NULL,
    end_sec INTEGER NOT NULL,
    winner VARCHAR(100),
    pot_size_bb FLOAT,
    is_all_in BOOLEAN NOT NULL DEFAULT FALSE,
    is_showdown BOOLEAN NOT NULL DEFAULT FALSE,
    cards_shown TEXT,
    board VARCHAR(50),
    grade hand_grade NOT NULL DEFAULT 'C',
    tags TEXT,
    highlight_score INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_hands_content_id ON hands(content_id);
CREATE INDEX idx_hands_grade ON hands(grade);

-- ============================================================================
-- Hand Players (Junction Table)
-- ============================================================================

CREATE TABLE hand_players (
    id SERIAL PRIMARY KEY,
    hand_id INTEGER NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    position VARCHAR(20),
    is_winner BOOLEAN NOT NULL DEFAULT FALSE,
    hole_cards VARCHAR(20)
);

CREATE INDEX idx_hand_players_hand_id ON hand_players(hand_id);
CREATE INDEX idx_hand_players_player_id ON hand_players(player_id);

-- ============================================================================
-- Watch Progress
-- ============================================================================

CREATE TABLE watch_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    progress_sec INTEGER NOT NULL DEFAULT 0,
    duration_sec INTEGER NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, content_id)
);

CREATE INDEX idx_watch_progress_user_id ON watch_progress(user_id);
CREATE INDEX idx_watch_progress_content_id ON watch_progress(content_id);

-- ============================================================================
-- View Events (Analytics)
-- ============================================================================

CREATE TABLE view_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    event_type event_type NOT NULL,
    position_sec INTEGER NOT NULL,
    metadata TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_view_events_user_id ON view_events(user_id);
CREATE INDEX idx_view_events_content_id ON view_events(content_id);
CREATE INDEX idx_view_events_created_at ON view_events(created_at);

-- ============================================================================
-- Initial Data
-- ============================================================================

-- Create admin user (password: Admin123!)
INSERT INTO users (username, password_hash, display_name, role, status)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.rR0F.ZvRj8KXZG',
    'Administrator',
    'admin',
    'approved'
);

-- Create sample catalogs
INSERT INTO catalogs (id, name, display_title, description, sort_order) VALUES
('wsop', 'WSOP', 'World Series of Poker', '세계 최대 포커 대회', 1),
('hcl', 'HCL', 'Hustler Casino Live', '허슬러 카지노 라이브', 2),
('pad', 'PAD', 'Poker After Dark', '포커 애프터 다크', 3),
('ggmillions', 'GGMillions', 'GG Millions', 'GG 밀리언즈', 4);

-- ============================================================================
-- Updated_at Trigger Function
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watch_progress_updated_at
    BEFORE UPDATE ON watch_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
