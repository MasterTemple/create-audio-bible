from dataclasses import dataclass
import subprocess
from mutagen import mp3
from mutagen.id3 import ID3, APIC, TIT2, TXXX, ID3NoHeaderError
from mutagen.mp3 import MP3
from vars import CURRENT_PROJECT_FILE, PROJECT_DIR, PROJECT_CONFIG_FILE_NAME, PROJECT_DIR_AUDIO
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

@dataclass
class SourceData:
    id: str
    start_time: float
    end_time: float
    volume: float
    extra: str = ""

def add_source_data(mp3_file: str, sd: SourceData):
    """
    Description:
      Adds source data to mp3 so I know how it was generated so I know if I need to regenerate it
    Parameters:
      mp3_file: str - Path to the MP3 file.
      note: str - The note to add.
    """
    audio = ID3(mp3_file)
    audio.add(TIT2(text=f"source=[{sd.id},{sd.start_time},{sd.end_time},{sd.volume},{json.dumps(extra)}]"))
    audio.save()

def read_source_data(mp3_file) -> SourceData:
    """
    Description:
      Reads source data from mp3 so I know how it was generated so I know if I need to regenerate it
    Args:
      mp3_file: str - Path to the MP3 file.
    Returns:
      str: Source data
    """
    audio = ID3(mp3_file)
    for frame in audio.getall("TIT2"):
        for text in frame.text:
            if text.startswith("source=["):
                elements = text[len("source=["):-1].split(",")
                return SourceData(
                    elements[0],
                    float(elements[1]),
                    float(elements[2]),
                    float(elements[3]),
                    elements[4],
                )
    return None

def embed_source_data(mp3_path: str, source_data: SourceData):
    if not os.path.exists(mp3_path):
        return
    try:
        audio = MP3(mp3_path, ID3=ID3)
    except ID3NoHeaderError:
        audio = MP3(mp3_path)
        audio.add_tags()
    
    # Convert SourceData to JSON string
    source_data_json = json.dumps(source_data.__dict__)
    
    # Add/Update TXXX frame for SourceData
    audio.tags.add(TXXX(desc='SourceData', text=source_data_json))
    
    # Save changes to the file
    audio.save()

def extract_source_data(mp3_path: str) -> SourceData:
    audio = MP3(mp3_path, ID3=ID3)
    
    # Retrieve the TXXX frame with description 'SourceData'
    source_data_frame = audio.tags.get('TXXX:SourceData')
    
    if source_data_frame:
        # Convert JSON string back to SourceData object
        source_data_dict = json.loads(source_data_frame.text[0])
        return SourceData(**source_data_dict)
    else:
        raise ValueError("No SourceData found in the given MP3 file.")

def merge_files(source_data: SourceData, files: list[str], bitrate=192) -> str:
    project_name = get_current_project()
    # print(PROJECT_DIR)
    # print(project_name)
    # print(PROJECT_DIR_AUDIO)
    # print(source_data.extra)
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_AUDIO, f'{source_data.extra}.mp3')
    print(output_file)
    if os.path.exists(output_file):
        previous_data = extract_source_data(output_file)
        if previous_data == source_data:
            return output_file

    print(f"Creating Merge")

    temp = f'{source_data}.txt'
    with open(temp, 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")

    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp, '-c', 'copy', '-b:a', f'{bitrate}k', '-c:a', 'libmp3lame', output_file, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    embed_source_data(output_file, source_data)
    # add_album_art(output_file)
    os.remove('list.txt')
    return output_file
