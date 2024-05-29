import pandas as pd
from sqlalchemy import create_engine

# Create a connection to MySQL
engine = create_engine('mysql://dgmastertemple:please@localhost/`Ephesians - Tim Conway`')

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('./projects/Ephesians - Tim Conway/csv/searches.csv')

# Insert the DataFrame into the MySQL table
df.to_sql('searches', con=engine, if_exists='append', index=False)
