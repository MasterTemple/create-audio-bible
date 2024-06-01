from mutagen.id3 import ID3, APIC
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


def add_album_art(input_file: str, cover_image: str):
    audio = ID3(input_file)
    with open(cover_image, 'rb') as image_file:
        image_data = image_file.read()
    mime='image/jpeg'
    if cover_image.endswith(".png"):
        mime='image/png'
    album_art = APIC(
        encoding=3,  # UTF-8
        mime=mime,
        type=3,  # Cover (front)
        desc='Cover (Front)',
        data=image_data
    )
    audio['APIC'] = album_art
    audio.save(input_file, v2_version=3)
