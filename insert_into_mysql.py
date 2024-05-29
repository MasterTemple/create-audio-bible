from time import sleep
import csv
import mysql.connector
import re
import sys
import os
from vars import CSV_SEARCHES_FILE, CSV_SEGMENTS_FILE, CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR
from functions import get_current_project
from dotenv import load_dotenv

load_dotenv()

def get_db_name():
    project_name = get_current_project()
    # return re.sub(r'[^A-z0-9]', '', project_name)
    return project_name

def cn(db=""):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            charset="utf8mb4",
            database=db
        )
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)
    return conn

def create_database():
    con = cn()
    db_name = get_db_name()
    cur = con.cursor()
    try:
        cur.execute("DROP SCHEMA `%s`", (db_name,))
    except:
        pass
    cur.execute("CREATE SCHEMA `%s`", (db_name,))
    # otherwise create_tables() fails
    sleep(2)
    # create_tables()

def create_tables():
    db_name = get_db_name()
    con = cn()
    cur = con.cursor()
    cur.execute("USE `%s`", (db_name,))
    with open("./create_tables.sql") as f:
        sql = f.read()
    cur.execute(sql)

def import_csv():
    db_name = get_db_name()
    csv_folder = os.path.join(PROJECT_DIR, db_name, PROJECT_CSV_DIR)
    con = cn()
    cur = con.cursor()
    cur.execute("USE `%s`", (db_name,))
    files = [CSV_SEARCHES_FILE, CSV_SEGMENTS_FILE, CSV_SEGMENTS_FILE]
    for file in files:
        table, _ = file.split(".")
        query = "\n".join(
            [
                f"LOAD DATA INFILE '{os.path.join(os.path.abspath('.'), csv_folder, file)}'",
                f"REPLACE INTO TABLE {table}",
                "FIELDS TERMINATED BY ','",
                "ENCLOSED BY '\"'",
                "LINES TERMINATED BY '\n'",
                "IGNORE 1 ROWS;",
            ]
        )
        print(query)
        cur.execute(query)

# create_database()
# create_tables()
# import_csv()

db_name = get_db_name()
csv_folder = os.path.join(PROJECT_DIR, db_name, PROJECT_CSV_DIR)
con = cn()
cur = con.cursor()
cur.execute("USE `%s`", (db_name,))
files = [CSV_SEARCHES_FILE, CSV_SEGMENTS_FILE, CSV_SEGMENTS_FILE]
file = CSV_SEARCHES_FILE
# path = os.path.join(os.path.abspath('.'), csv_folder, file)
path = os.path.join(csv_folder, file)
# Open the CSV file
import pandas as pd
df = pd.read_csv(path)
insert_stmt = "INSERT INTO searches (id, value) VALUES (%s, %s)"
tuples = []
for i, row in df.iterrows():
    tuples.append((row[0], row[1]))
cur.executemany(insert_stmt, tuples)

# Commit the changes and close the connection
con.commit()
cur.close()
con.close()
