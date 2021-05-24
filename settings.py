import os
from dotenv import load_dotenv

load_dotenv()

SETTINGS = {
  'CHANNEL_SECRET': os.environ.get('CHANNEL_SECRET', None),
  'CHANNEL_ACCESS_TOKEN': os.environ.get('CHANNEL_ACCESS_TOKEN', None),
  'DB_HOST': os.environ.get('DB_HOST', None),
  'DB_NAME': os.environ.get('DB_NAME', None),
  'DB_USER': os.environ.get('DB_USER', None),
  'DB_PASS': os.environ.get('DB_PASS', None)
}