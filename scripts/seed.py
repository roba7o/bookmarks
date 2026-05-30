import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


# Connecting to database

conn = psycopg2.connect(
    password=os.getenv("DB_PASSWORD"),
    user=os.getenv("DB_USER"),
    database=os.getenv("DB_NAME"),
    host="localhost",
    port=5432,
)


cur = conn.cursor()

cur.execute(open("SQL/02-GEN_SAMPLE_DATA.sql").read())

conn.commit()

cur.close()

conn.close()
