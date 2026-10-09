
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

# Load .env from the same folder as database.py
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Check configuration without displaying your password
print("ENV file exists:", env_path.exists())
print("DB_HOST:", repr(os.getenv("DB_HOST")))
print("DB_USER:", repr(os.getenv("DB_USER")))
print("DB_NAME:", repr(os.getenv("DB_NAME")))
print("DB_PASSWORD loaded:", bool(os.getenv("DB_PASSWORD")))

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

print("MySQL connection established")
