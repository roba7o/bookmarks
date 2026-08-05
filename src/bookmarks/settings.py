import logging
import os

from dotenv import load_dotenv

load_dotenv()

# configuring logging globally.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Database env
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

# tokens env

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = os.environ["JWT_ALGORITHM"]
