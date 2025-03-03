from dotenv import load_dotenv
import os

load_dotenv('.env')

PGSQL_PASSWORD = os.getenv('PGSQL_PASSWORD')
PGSQL_USERNAME = os.getenv('PGSQL_USERNAME')
PGSQL_HOST = os.getenv('PGSQL_HOST')
