-- 1. Create the Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL -- In a real app, this would be a hash!
);

-- 2. Create the Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_username VARCHAR(50) REFERENCES users(username) ON DELETE CASCADE,
    receiver_username VARCHAR(50) REFERENCES users(username) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);