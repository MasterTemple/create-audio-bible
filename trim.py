import os
import subprocess
from functions import get_current_project

from vars import AUDIO_TRIM_DIR, CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE

def trim_file(id: str, start_time: float, end_time: float, volume: float=1.0):
    project_name = get_current_project()
    input_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f'{id}.mp3')
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_AUDIO, AUDIO_TRIM_DIR, f'{id}-{start_time}-{end_time}-{volume}.mp3')
    if not os.path.exists(output_file):
        command = ['ffmpeg', '-loglevel', 'error', '-i', input_file, '-ss', str(start_time),
                   '-to', str(end_time), '-af', f'volume={volume}', '-c:a', 'libmp3lame', output_file]
        subprocess.run(command)
    with open(output_file, "rb") as f:
        return f.read()


trim_file("11719173237194", 118.996, 133.423)
