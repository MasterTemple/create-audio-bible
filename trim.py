import os
import json
import subprocess
from functions import get_current_project
from dataclasses import dataclass

@dataclass
class Reading:
    id: str
    start_time: float
    end_time: float
    start_seg: int
    end_seg: int
    content: str

from vars import JSON_READINGS_FILE, PROJECT_DIR_AUDIO_TRIM, CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE, PROJECT_JSON_DIR

def trim_file(project_name: str, id: str, start_time: float, end_time: float, volume: float=1.0, bitrate: int=192) -> str:
    # project_name = get_current_project()
    input_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f'{id}.mp3')
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_AUDIO, f'{id},{start_time},{end_time},{volume}.mp3')
    if not os.path.exists(output_file):
        command = ['ffmpeg', '-loglevel', 'error', '-i', input_file, '-ss', str(start_time),
                   '-to', str(end_time), '-af', f'volume={volume}', '-b:a', f'{bitrate}k', '-c:a', 'libmp3lame', output_file, "-y"]
        subprocess.run(command)
    return output_file
    # with open(output_file, "rb") as f:
    #     return f.read()


# trim_file("11719173237194", 118.996, 133.423)

def trim_all_findings():
    project_name = get_current_project()
    with open(os.path.join(PROJECT_DIR, project_name, PROJECT_JSON_DIR, JSON_READINGS_FILE), "r") as f:
        data = json.load(f)
    break_stop = 5
    for ref, finds in data.items():
        early_break = False
        for i, r in enumerate(finds):
            if i == break_stop:
                early_break = True
                break
            print(f"Trimming files for {ref}: [{i+1}/{len(finds)}]", end="\r")
            reading = Reading(**r)
            trim_file(project_name, reading.id, reading.start_time, reading.end_time)
        if early_break:
            print(f"Trimming files for {ref}: [{5}/{len(finds)}]")
        else:
            print(f"Trimming files for {ref}: [{len(finds)}/{len(finds)}]")
