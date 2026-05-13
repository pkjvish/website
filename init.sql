CREATE DATABASE IF NOT EXISTS crud_db;
USE crud_db;

DROP TABLE IF EXISTS tbl_user;

CREATE TABLE tbl_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(45) NOT NULL,
    user_age INT NOT NULL,
    user_email VARCHAR(45) NOT NULL UNIQUE
);

-- Insert starting sample data matching the new layout
INSERT INTO tbl_user (user_name, user_age, user_email) VALUES 
('Pankaj Kumar', 28, 'pankaj@example.com'),
('Jane Doe', 34, 'jane@example.com');
