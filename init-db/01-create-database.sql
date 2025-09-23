-- Database initialization script
-- Creates the main database and user if they don't exist

-- Create database for production
SELECT 'CREATE DATABASE saas_cafeterias_prod'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'saas_cafeterias_prod')\gexec

-- Create database for staging
SELECT 'CREATE DATABASE saas_cafeterias_staging'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'saas_cafeterias_staging')\gexec

-- Create database for development
SELECT 'CREATE DATABASE saas_cafeterias'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'saas_cafeterias')\gexec

-- Grant all privileges to users
GRANT ALL PRIVILEGES ON DATABASE saas_cafeterias TO saasuser;
GRANT ALL PRIVILEGES ON DATABASE saas_cafeterias_staging TO saasuser;
GRANT ALL PRIVILEGES ON DATABASE saas_cafeterias_prod TO saasuser;