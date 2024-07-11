import os
import psycopg2

# Ładowanie zmiennych środowiskowych z pliku env.py
if os.path.exists("env.py"):
    import env  # noqa

# Debugowanie zmiennych środowiskowych
print("Environment Variables:")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")

# Połączenie do bazy danych
try:
    connection = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'project'),
        user=os.getenv('DB_USER', 'postgres'),
        host=os.getenv('DB_HOST', 'localhost'),
        password=os.getenv('DB_PASSWORD', 'your_actual_password')
    )
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
