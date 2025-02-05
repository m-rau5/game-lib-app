import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI_ENV = os.getenv("MONGO_URI")


class Config:
    MONGO_URI = MONGO_URI_ENV
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_CLIENT_ID = os.getenv('CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
