import os
import json
import sys
import shutil

CURRENT_PROJECT_FILE = ".current_project.txt"

DATA_DIR = "data/"
PROJECT_DIR = DATA_DIR + "projects/"
PROJECT_DIR_AUDIO = "audio/"
PROJECT_DIR_EXPORT = "export/"
PROJECT_DIR_EXPORT_VERSES = PROJECT_DIR_EXPORT + "verses/"
PROJECT_DIR_EXPORT_CHAPTERS = PROJECT_DIR_EXPORT + "chapters/"
PROJECT_CONFIG_FILE_NAME = "config.json"
TRANSCRIPTS_DIR = DATA_DIR + "transcripts/"
DOWNLOADS_DIR = DATA_DIR + "downloads/"
TEMP_DOWNLOADS_DIR = DATA_DIR + "downloads/temp/"

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

def main():
    if len(sys.argv) < 2:
        print("Usage: cab <command> [arguments]")
        print("Usage: cab create <project-name> <book> <sources.txt>")
        print("Usage: cab use <project-name>")
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
