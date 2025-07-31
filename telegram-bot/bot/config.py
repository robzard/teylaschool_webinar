import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

if ADMIN_ID:
    ADMIN_IDS_LIST = [int(id.strip()) for id in ADMIN_ID.split(',')]
else:
    raise ValueError("ADMIN_IDS не установлен в переменных окружения")
