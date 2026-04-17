-- 1. Stations Table
CREATE TABLE stations (
    station_id      INTEGER PRIMARY KEY,
    station_name    VARCHAR2(100) NOT NULL,
    location_address VARCHAR2(255),
    total_ports     INTEGER
);

-- 2. Station Details Table (1:1 Relationship with Stations)
CREATE TABLE station_details (
    station_id      INTEGER PRIMARY KEY,
    network_type    VARCHAR2(50),
    max_voltage     INTEGER,
    CONSTRAINT fk_details_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- 3. Users Table
CREATE TABLE users (
    user_id         INTEGER PRIMARY KEY,
    email           VARCHAR2(100) NOT NULL,
    phone_number    VARCHAR2(20)
);

-- 4. Maintenance Logs Table (Many-to-One with Stations)
CREATE TABLE maintenance_logs (
    log_id          INTEGER PRIMARY KEY,
    station_id      INTEGER NOT NULL,
    issue_description TEXT,
    CONSTRAINT fk_logs_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- 5. Charging Sessions Table (Links Users and Stations)
CREATE TABLE charging_sessions (
    session_id      INTEGER PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    station_id      INTEGER NOT NULL,
    energy_consumed_kwh DECIMAL(10, 2),
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_session_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
);
