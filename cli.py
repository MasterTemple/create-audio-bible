import os
import json
import sys
import download
# import transcribe

from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, TRANSCRIPTS_DIR, DOWNLOADS_DIR, TEMP_DOWNLOADS_DIR


def create_project(project_name, book, sources_file):
    new_project_dir = os.path.join(os.getcwd(), PROJECT_DIR, project_name)
    if os.path.exists(new_project_dir):
        print(f"Error: Project '{project_name}' already exists.")
        return

    os.makedirs(new_project_dir)
    os.makedirs(os.path.join(new_project_dir, PROJECT_DIR_AUDIO))
    os.makedirs(os.path.join(new_project_dir, PROJECT_DIR_EXPORT))
    os.makedirs(os.path.join(new_project_dir, PROJECT_DIR_EXPORT_VERSES))
    os.makedirs(os.path.join(new_project_dir, PROJECT_DIR_EXPORT_CHAPTERS))

    with open(sources_file, 'r') as f:
        sources = [s.strip() for s in f.read().splitlines()]

    with open(os.path.join(new_project_dir, PROJECT_CONFIG_FILE_NAME), "w") as f:
        f.write(json.dumps({
            "name": project_name,
            "book": book,
            "cover_image": "/path/to/img", # I'll deal with this later
            "sources": sources
        }))

    print(f"Project '{project_name}' created successfully.")

    use_project(project_name)

def use_project(project_name):
    cur_project_dir = os.path.join(os.getcwd(), PROJECT_DIR, project_name)
    if not os.path.exists(cur_project_dir):
        print(f"Error: Project '{project_name}' does not exist.")
        return

    with open(CURRENT_PROJECT_FILE, "w") as f:
        f.write(project_name)
    print(f"Now using project '{project_name}'.")

def get_current_project() -> str:
    with open(CURRENT_PROJECT_FILE, "r") as f:
        project_name = f.read()
    return project_name

def download_project_files() -> None:
    project_name = get_current_project()
    download.download_project_files(project_name)

def transcribe_project_files() -> None:
    # project_name = get_current_project()
    # transcribe.transcribe_project_files(project_name)
    # transcribe.transcribe_all_files()
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: cab <command> [arguments]")
        print("Usage: cab create <project-name> <book> <sources.txt>")
        print("Usage: cab use <project-name>")
        print("Usage: cab download")
        print("Usage: cab transcribe")
        return

    command = sys.argv[1]
    if command == "create":
        if len(sys.argv) != 5:
            print("Usage: cab create <project-name> <book> <sources.txt>")
            return
        project_name = sys.argv[2]
        book = sys.argv[3]
        sources_file = sys.argv[4]
        create_project(project_name, book, sources_file)
    elif command == "download":
        download_project_files()
    elif command == "transcribe":
        transcribe_project_files()
    elif command == "use":
        if len(sys.argv) != 3:
            print("Usage: cab use <project-name>")
            return
        project_name = sys.argv[2]
        use_project(project_name)
    else:
        print(f"Error: Invalid command '{command}'.")

if __name__ == "__main__":
    main()
