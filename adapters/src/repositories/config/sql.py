import os


class SQLConfig:
    DB_CONFIG = os.environ.get("DATABASE_URL") #changing SQL_URL to DATABASE_URL
