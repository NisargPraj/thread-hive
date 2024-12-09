CREATE DATABASE IF NOT EXISTS admin_service_db;
USE admin_service_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON admin_service_db.* TO 'root'@'%';
FLUSH PRIVILEGES;
