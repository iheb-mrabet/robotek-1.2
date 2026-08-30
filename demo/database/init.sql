CREATE TABLE robot_status (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    status VARCHAR(24) NOT NULL,
    battery INTEGER NOT NULL CHECK (battery BETWEEN 0 AND 100),
    mission VARCHAR(120) NOT NULL,
    destination VARCHAR(120) NOT NULL,
    completed_deliveries INTEGER NOT NULL DEFAULT 0,
    release VARCHAR(80) NOT NULL
);

INSERT INTO robot_status (
    name,
    status,
    battery,
    mission,
    destination,
    completed_deliveries,
    release
) VALUES (
    'Robotek-01',
    'ONLINE',
    87,
    'Warehouse delivery',
    'Dock B',
    12,
    'base-v1'
);
