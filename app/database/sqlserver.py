import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_sqlserver_connection():
    connection_string = (
        f"DRIVER={{{os.getenv('SQL_DRIVER')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USER')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )

    connection = pyodbc.connect(connection_string)

    return connection