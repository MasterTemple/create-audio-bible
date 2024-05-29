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
