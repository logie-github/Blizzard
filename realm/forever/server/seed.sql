-- The Forever realm on the phone: what the app adds to TrinityCore's databases as the package makes them
-- (scripts/package-trinity-forever.sh).

-- The account the realm's programs and the app use, on 127.0.0.1 only (ctl.sh's DB_USER).
CREATE USER IF NOT EXISTS 'forever'@'127.0.0.1' IDENTIFIED BY 'forever';
CREATE USER IF NOT EXISTS 'forever'@'localhost' IDENTIFIED BY 'forever';
GRANT ALL PRIVILEGES ON `auth`.* TO 'forever'@'127.0.0.1', 'forever'@'localhost';
GRANT ALL PRIVILEGES ON `characters`.* TO 'forever'@'127.0.0.1', 'forever'@'localhost';
GRANT ALL PRIVILEGES ON `world`.* TO 'forever'@'127.0.0.1', 'forever'@'localhost';
GRANT ALL PRIVILEGES ON `hotfixes`.* TO 'forever'@'127.0.0.1', 'forever'@'localhost';
GRANT SHUTDOWN ON *.* TO 'forever'@'127.0.0.1', 'forever'@'localhost';
FLUSH PRIVILEGES;
