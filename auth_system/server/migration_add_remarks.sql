-- Migration script to add remarks, monitor_cookie, and monitor_urls columns to auth_requests table
-- Run this SQL in your D1 database console if the table already exists

-- ALTER TABLE auth_requests ADD COLUMN remarks TEXT;
ALTER TABLE auth_requests ADD COLUMN monitor_cookie TEXT;
ALTER TABLE auth_requests ADD COLUMN monitor_urls TEXT;

-- Optional: Add indexes if needed for search functionality
-- CREATE INDEX idx_remarks ON auth_requests(remarks);
-- CREATE INDEX idx_monitor_cookie ON auth_requests(monitor_cookie);