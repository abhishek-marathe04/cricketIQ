from dotenv import load_dotenv
import os

load_dotenv()

ENV = os.getenv("ENV", "local")
IS_PROD = os.getenv("ENV", "local") == "prod"
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-XXXXXXXXXX")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")