import os
SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# TODO IMPLEMENT DATABASE URL
db_base_url=os.environ.get("DB_BASE_UR", "localhost:5432")
db_username=os.environ.get("DB_USERNAME", "postgres")
db_password=os.environ.get("DB_PASSWORD", "")
db_name=os.environ.get("DB_NAME", "fyyur")

SQLALCHEMY_DATABASE_URI = f"postgresql://{db_username}:{db_password}@{db_base_url}/{db_name}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
