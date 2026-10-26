CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    gender      VARCHAR(20)  NOT NULL,
    age         INTEGER      NOT NULL,
    dob         DATE         NOT NULL,
    address     TEXT         NOT NULL,
    blood_group VARCHAR(5)   NOT NULL,
    time_zone   VARCHAR(64)  NOT NULL
);