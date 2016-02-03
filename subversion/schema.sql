
-- To create the database:
--   CREATE DATABASE subversion;
--   GRANT ALL PRIVILEGES ON subversion.* TO 'subversion'@'localhost' IDENTIFIED BY 'subversion';
--
-- To reload the tables:
--   mysql --user=subversion --password=subversion --database=subversion < schema.sql

SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL REFERENCES authors(id),
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL,
    repo VARCHAR(512) NOT NULL,
    username VARCHAR(128) NOT NULL,
    password VARCHAR(128) NOT NULL,
    host VARCHAR(128) NOT NULL,
    dest VARCHAR(512) NOT NULL,
    revision VARCHAR(128) NOT NULL,
    published DATETIME NOT NULL,
    updated TIMESTAMP NOT NULL,
    KEY (published)
);

DROP TABLE IF EXISTS authors;
CREATE TABLE authors (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(100) NOT NULL
);
