CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    gender      VARCHAR(20),
    age         INTEGER,
    dob         DATE,
    address     TEXT,
    blood_group VARCHAR(5),
    time_zone   VARCHAR(64)
);