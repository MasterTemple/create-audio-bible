"""
Create Audio Bible API
Endpoints:
    POST: /esv(book, chapter, verse) -> content
    GET : /config() -> config{}
    GET : /readings() -> readings
    POST: /audio(file_id, start_time, end_time, volume) -> .mp3
    POST: /export(book_tree) -> .mp3 | .zip
    POST: /save(book_tree) -> None
"""

import re
from functools import lru_cache
import os
import sqlite3
from textwrap import indent
from flask import Flask, Response, request, send_file, jsonify
import subprocess
from io import BytesIO
from flask_cors import CORS
import json
from functions import get_project_config, get_db_name, get_current_project
from find_readings import get_esv_book, get_esv_content
from trim import trim_file
from vars import JSON_READINGS_FILE, PROJECT_CONFIG_FILE_NAME, PROJECT_DIR, PROJECT_DIR_EXPORT, PROJECT_JSON_DIR, JSON_READINGS_FILE_EDITED, PROJECT_DOWNLOADS_DIR, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS
from pymongo import MongoClient
from dataclasses import dataclass


# client = MongoClient('mongodb://localhost:27017/')
# db = client[get_db_name()]
# searches = {s["word"]: s["segments"] for s in db["searches"].find({})}
# segments = {s["id"]: s for s in db["segments"].find({})}

path = "ESV.sqlite"

app = Flask(__name__)
app.config['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
CORS(app)

#############
# FUNCTIONS #
#############

def reply(data):
    res = jsonify(data)
    res.headers.set("Content-Type", "application/json")
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

#################
# SERVER ROUTES #
#################

@app.route('/verse', methods=['POST'])
def verse():
    """
    Description:
        Get the contents of a Bible verse from reference (in ESV)
    Parameters:
        book: str
        chapter: int
        verse: int
    Returns:
        content: str
    """
    data: dict = request.json
    content = get_esv_content(data['book'], data['chapter'], data['verse'])
    return reply({
        "book": data['book'],
        "chapter": data['chapter'],
        "verse": data['verse'], 
        "content": content
    })

@app.route('/esv', methods=['POST'])
def esv():
    """
    Description:
        Get the ESV contents of a book in the Bible
    Parameters:
        book: str
    Returns:
        reference_to_content: dict[str, str] - reference to reference content
    """
    data: dict = request.json
    reference_to_content = get_esv_book(data['book'])
    return reply(reference_to_content)

@app.route('/config', methods=['GET'])
def config():
    """
    Description:
        Get the config.json file of the current project
    Parameters:
    Returns:
        config: {} - the contents of config.json
    """
    return reply(get_project_config())

@lru_cache()
@app.route('/readings', methods=['GET'])
def readings():
    """
    Description:
        Get the readings.json file
    Parameters:
    Returns:
        book_tree
    """
    readings_edited_path = os.path.join(PROJECT_DIR, get_current_project(), PROJECT_JSON_DIR, JSON_READINGS_FILE_EDITED)
    readings_unedited_path = os.path.join(PROJECT_DIR, get_current_project(), PROJECT_JSON_DIR, JSON_READINGS_FILE)
    file = readings_unedited_path

    if os.path.exists(readings_edited_path):
            file = readings_edited_path

    with open(file, "r") as f:
        data = json.load(f)
    return reply(data)

@app.route('/file', methods=['GET'])
def file():
    """
    Description:
    Parameters:
        file_id: str
    Returns:
        file.mp3
    """
    project_name = get_current_project()
    id = request.args.get("id")
    file_path = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f'{id}.mp3')
    if os.path.isfile(file_path):
        return send_file(file_path, mimetype="audio/mpeg")
    else:
        return "File not found", 404

@app.route('/audio', methods=['GET'])
def audio():
    """
    Description:
    Parameters:
        file_id: str
        start_time: float
        end_time: float
        volume: float = 1
    Returns:
        file.mp3
    """
    project_name = get_current_project()

    # print(
    #     request.args.get("file_id"),
    #     request.args.get("start_time"),
    #     request.args.get("end_time"),
    #     request.args.get("volume") or 1
    # )

    output_path = trim_file(
        project_name,
        request.args.get("file_id"),
        request.args.get("start_time"),
        request.args.get("end_time"),
        request.args.get("volume") or 1
    )
    with open(output_path, "rb") as f:
        return f.read()

@dataclass
class Reference:
    book: str
    chapter: int
    verse: int
    @property
    def fmt_chapter(self):
        return f"{self.book} {self.chapter}"
    @property
    def fmt_verse(self):
        return f"{self.book} {self.chapter}:{self.verse}"

@dataclass
class Reading:
    id: str
    start_time: float
    end_time: float
    start_seg: int
    end_seg: int
    content: str
    use: bool
    volume: float
    ref: Reference

def create_verse_audio_file(config: dict[str,str], reading: Reading, track_number: int, bitrate: int=192) -> str:
    project_name = config["name"]
    ref = reading.ref
    input_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f'{reading.id}.mp3')
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_VERSES, f'{ref.fmt_verse} - {config["author"]}.mp3')

    metadata_tags = [
        '-metadata', f'title={ref.fmt_verse}',
        '-metadata', f'track={track_number}',
        '-metadata', f'album={config["book"]} - Verses',
        '-metadata', f'artist={config["author"]}'
    ]

    if not os.path.exists(output_file):
        command = ['ffmpeg', '-loglevel', 'error', '-i', input_file, '-ss', str(reading.start_time), '-to', str(reading.end_time), '-af', f'volume={reading.volume}', *metadata_tags, '-b:a', f'{bitrate}k', '-c:a', 'libmp3lame', output_file, "-y"]

        # cmd = ['ffmpeg', '-loglevel', 'error', '-i', mp3_path, '-ss', start_time, '-to', end_time, '-af', f'volume={volume_level}', *metadata_tags, '-c:a', 'libmp3lame', output_path, '-y']
        subprocess.run(command)
    return output_file
    # with open(output_file, "rb") as f:
    #     return f.read()

@app.route('/export', methods=['POST'])
def export():
    """
    Description:
    Parameters:
    (book_tree) -> .mp3 | .zip
    """
    config = get_project_config()
    project_name = get_current_project()
    # pro move, create symbolic link from selected .mp3 to exported new .mp3 (though modify the image if necessary)

    data: dict = request.json
    book_tree = data["book_tree"]
    export_type = data["export_type"]

    reading_list = []
    for chapter, references_to_readings in book_tree.items():
        for reference, readings in references_to_readings.items():
            ref = Reference(
                re.search(r".*(?= \d+:)", reference)[0],
                int(re.search(r"\d+(?=:)", reference)[0]),
                int(re.search(r"\d+$", reference)[0])
            )
            for r in readings:
                reading = Reading(
                    id=r["id"],
                    start_time=r["start_time"],
                    end_time=r["end_time"],
                    start_seg=r["start_seg"],
                    end_seg=r["end_seg"],
                    content=r["content"],
                    use=r["use"],
                    volume=r["volume"],
                    ref=ref
                )
                if reading.use:
                    reading_list.append(reading)

    track_number = 1

    def get_chapter_and_verse(s):
        l = list(map( lambda i: int(i), re.findall(r'\d+', s)[:-1][-2:]))
        return l

    # sort mp3 files by chapter and verse
    reading_list_sorted = sorted(reading_list, key= lambda r: [r.ref.chapter, r.ref.verse])

    for reading in reading_list_sorted:
        create_verse_audio_file(config, reading, track_number)
        track_number += 1
        break
    return reply({})

@app.route('/save', methods=['POST'])
def save():
    """
    Description:
    Parameters:
        book_tree: []
    Returns:
    """
    data: dict = request.json
    book_tree = data["book_tree"]

    readings_json = {}

    for chapter, references_to_readings in book_tree.items():
        for reference, readings in references_to_readings.items():
            readings_json[reference] = []
            for reading in readings:
                readings_json[reference].append({
                  "id": reading["id"],
                  "start_time": reading["start_time"],
                  "end_time": reading["end_time"],
                  "start_seg": reading["start_seg"],
                  "end_seg": reading["end_seg"],
                  "content": reading["content"],
                  "use": reading["use"],
                  "volume": reading["volume"],
                })

    readings_edited_path = os.path.join(PROJECT_DIR, get_current_project(), PROJECT_JSON_DIR, JSON_READINGS_FILE_EDITED)
    with open(readings_edited_path, "w") as f:
        f.write(json.dumps(readings_json, indent=2))
    return reply({})

if __name__ == '__main__':
    # host server
    app.run(debug=True) # ssl_context='adhoc'
