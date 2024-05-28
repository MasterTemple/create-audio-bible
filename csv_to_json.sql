-- search `/mnt/windows/Users/dgmastertemple/.vscode/sermon_indexing/sermon_indexing/sermon_transcription`
-- should be project name
set @db_name = '%s';
set @csv_path = '%s';

-- ! so i can overwrite it to make a change, maybe delete later
DROP SCHEMA @db_name;

-- create database
CREATE SCHEMA @db_name;
USE @db_name;

-- create tables
CREATE TABLE sources (
	-- id for this db only
	id INT PRIMARY KEY,
	-- actual id
	value TEXT
	-- everything else is valuable, but not for the sake of this project
);

CREATE TABLE segments (
	id INT PRIMARY KEY,
	source INT,
	content TEXT,
	start FLOAT,
	end FLOAT,
	sequence INT,
	FOREIGN KEY (source) REFERENCES sources(id)
);

CREATE TABLE searches (
	id INT AUTO_INCREMENT PRIMARY KEY,
	word TEXT,
	segments LONGTEXT
);

-- utf-8
ALTER DATABASE sermon_indexing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE segments MODIFY content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE searches MODIFY word TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- load CSV data
-- look into `CONCAT_PATH()`
LOAD DATA INFILE 'C:\\Users\\dgmastertemple\\.vscode\\sermon_indexing\\sermon_indexing\\sermon_transcription\\csv\\sources.csv'
INTO TABLE sources
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\dgmastertemple\\.vscode\\sermon_indexing\\sermon_indexing\\sermon_transcription\\csv\\segments.csv'
INTO TABLE segments
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

delete from searches;
LOAD DATA INFILE 'C:\\Users\\dgmastertemple\\.vscode\\sermon_indexing\\sermon_indexing\\sermon_transcription\\csv\\searches.csv'
INTO TABLE searches
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(word, segments);

select count(*) from sources;
select count(*) from segments;
select count(*) from searches;

