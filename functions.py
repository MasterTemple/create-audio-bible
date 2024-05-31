from vars import CURRENT_PROJECT_FILE, PROJECT_DIR, PROJECT_CONFIG_FILE_NAME
import re
import os
import json

def get_current_project() -> str:
    with open(CURRENT_PROJECT_FILE, "r") as f:
        project_name = f.read()
    return project_name

def get_project_config() -> dict:
    with open(os.path.join(PROJECT_DIR, get_current_project(), PROJECT_CONFIG_FILE_NAME), "r") as f:
        data = json.loads(f.read())
    return data

def get_db_name() -> str:
    return re.sub(" ", "_", get_current_project())
