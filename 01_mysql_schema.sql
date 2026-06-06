-- Job Market Analytics Platform - MySQL Schema
-- Create database
CREATE DATABASE IF NOT EXISTS job_market_db;
USE job_market_db;

-- 1. Companies table
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_description LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Locations table
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(50),
    UNIQUE KEY unique_location (city, state, country),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Jobs table (main table)
CREATE TABLE jobs (
    job_id VARCHAR(100) PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    company_id INT,
    location_id INT,
    job_description LONGTEXT,
    job_type VARCHAR(50),
    is_remote BOOLEAN DEFAULT FALSE,
    posting_date DATE,
    job_link VARCHAR(500),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_posting_date (posting_date),
    INDEX idx_job_title (job_title),
    INDEX idx_company_id (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Skills table
CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Job_Skills junction table (many-to-many relationship)
CREATE TABLE job_skills (
    job_skill_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    skill_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE KEY unique_job_skill (job_id, skill_id),
    INDEX idx_job_id (job_id),
    INDEX idx_skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE INDEX idx_jobs_location_type ON jobs(location_id, job_type);
CREATE INDEX idx_jobs_category ON jobs(category);
