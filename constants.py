from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
TABLE_NAME = os.environ.get("TABLE_NAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")