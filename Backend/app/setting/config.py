import re
import os

from os import pardir
from os.path import join, abspath, dirname

# Base directories
CURRENT_DIR = abspath(dirname(__file__))
APP_DIR = abspath(join(CURRENT_DIR, pardir))
SETTING_DIR = abspath(join(APP_DIR, "setting"))


class BaseConfig(object):
    VERSION = "v1"
    REST_API_URL = "api"
    # SQLITE_FILE_PATH = abspath(join(DATA_DIR, "sqlite_db.db"))
    URL_REGEX = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
    )

    PGDATABASE = os.getenv("PGDATABASE")
    PGHOST = os.getenv("PGHOST")
    PGPASSWORD = os.getenv("PGPASSWORD")
    PGPORT = 7747
    PGUSER = os.getenv("PGUSER")

CONFIGS = BaseConfig()
