from vars import CURRENT_PROJECT_FILE

def get_current_project() -> str:
    with open(CURRENT_PROJECT_FILE, "r") as f:
        project_name = f.read()
    return project_name

