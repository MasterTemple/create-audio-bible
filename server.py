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

import zipfile
import re
from functools import lru_cache
import os
import sqlite3
from textwrap import indent
from flask import Flask, Response, request, send_file, jsonify, abort
import subprocess
from io import BytesIO
from flask_cors import CORS
import json
from functions import add_album_art, add_source_data, get_project_config, get_db_name, get_current_project, read_source_data, SourceData, embed_source_data, extract_source_data
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

def create_verse_audio_file(cfg: dict[str,str], reading: Reading, track_number: int, overwrite=True, bitrate: int=192) -> str:
    project_name = cfg["name"]
    ref = reading.ref
    input_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f'{reading.id}.mp3')
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_VERSES, f'{ref.fmt_verse} - {cfg["author"]}.mp3')

    source_data = SourceData(reading.id, reading.start_time, reading.end_time, reading.volume)
    if os.path.exists(output_file):
        previous_data = extract_source_data(output_file)
        if previous_data == source_data:
            print(f"Skipping '{ref.fmt_verse}'")
            return output_file
    # if os.path.exists(output_file) and read_source_data(output_file) == source_data:
    #     return output_file


    metadata_tags = [
        '-metadata', f'title={ref.fmt_verse}',
        '-metadata', f'track={track_number}',
        '-metadata', f'album={cfg["book"]} - Verses',
        '-metadata', f'artist={cfg["author"]}'
    ]

    cover_image = os.path.join(os.path.abspath("."), cfg["cover_image"])
    print(cover_image)
    image_tags = [
        '-i', cover_image,
        '-map', '0:0',  # Map input audio stream
        '-map', '1:0',  # Map input cover image
        '-c', 'copy',
        '-metadata:s:v', 'title="Album cover"',
        '-metadata:s:v', 'comment="Cover (Front)"',
        '-metadata:s:v', 'mimetype=image/jpeg',
        '-metadata:s:v', f'cover={cover_image}',
        '-id3v2_version', '3',
    ]

    command = [
        'ffmpeg', '-loglevel', 'error',
        '-i', input_file,  # Input audio file
        '-ss', str(reading.start_time),
        '-to', str(reading.end_time),
        '-af', f'volume={reading.volume}',  # Audio filter
        # *image_tags,  # Image tags
        *metadata_tags,  # Metadata tags
        '-b:a', f'{bitrate}k',  # Audio bitrate
        '-c:a', 'libmp3lame',  # Audio codec
        output_file,  # Output file
        '-y'
    ]

    subprocess.run(command)
    embed_source_data(output_file, source_data)
    return output_file

def create_chapter_audio_file(cfg: dict[str,str], files_to_join: list[str], reading: Reading, overwrite:bool = True, bitrate: int=192) -> str:
    project_name = cfg["name"]
    ref = reading.ref
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_CHAPTERS, f'{ref.fmt_chapter} - {cfg["author"]}.mp3')
    if os.path.exists(output_file) and not overwrite:
        return output_file

    with open('list.txt', 'w') as f:
        for file in files_to_join:
            f.write(f"file '{file}'\n")

    metadata_tags = [
        '-metadata', f'title={ref.fmt_chapter}',
        '-metadata', f'track={ref.chapter}',
        '-metadata', f'album={cfg["book"]} - Chapters',
        '-metadata', f'artist={cfg["author"]}'
    ]

    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', *metadata_tags, '-b:a', f'{bitrate}k', '-c:a', 'libmp3lame', output_file, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # add_album_art(output_file)
    os.remove('list.txt')


def create_book_audio_file(cfg: dict[str,str], files_to_join: list[str], reading: Reading, overwrite:bool = True, bitrate: int=192) -> str:
    project_name = cfg["name"]
    ref = reading.ref
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT, f'{ref.book} - {cfg["author"]}.mp3')

    with open('list.txt', 'w') as f:
        for file in files_to_join:
            f.write(f"file '{file}'\n")

    metadata_tags = [
        '-metadata', f'title={ref.book}',
        '-metadata', f'track={ref.chapter}',
        '-metadata', f'album={cfg["book"]} - Chapters',
        '-metadata', f'artist={cfg["author"]}'
    ]

    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', *metadata_tags, '-b:a', f'{bitrate}k', '-c:a', 'libmp3lame', output_file, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # add_album_art(output_file)
    os.remove('list.txt')

@app.route('/export', methods=['POST'])
def export():
    """
    Description:
    Parameters:
    (book_tree) -> .mp3 | .zip
    """
    cfg = get_project_config()
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

    # sort mp3 files by chapter and verse
    reading_list_sorted: list[Reading] = sorted(reading_list, key= lambda r: [r.ref.chapter, r.ref.verse])

    for reading in reading_list_sorted:
        create_verse_audio_file(cfg, reading, track_number, False)
        track_number += 1

    if export_type == "chapters" or export_type == "book":
        chapter_count = max([r.ref.chapter for r in reading_list_sorted])
        chapter_map = {}
        for i in range(1, chapter_count + 1):
            chapter_map[i] = []
        for reading in reading_list_sorted:
            chapter_map[reading.ref.chapter].append(reading)
        for chapter, readings in chapter_map.items():
            pass
            files_to_join = []
            for reading in readings:
                output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_VERSES, f'{reading.ref.fmt_verse} - {cfg["author"]}.mp3')
                files_to_join.append(output_file)
            create_chapter_audio_file(cfg, files_to_join, readings[0], False)

    if export_type == "book":
        chapter_count = max([r.ref.chapter for r in reading_list_sorted])
        files_to_join = []
        reading = reading_list_sorted[0]
        for i in range(1, chapter_count + 1):
            output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_CHAPTERS, f'{reading.ref.fmt_chapter} - {cfg["author"]}.mp3')
            files_to_join.append(output_file)
        create_book_audio_file(cfg, files_to_join, reading, False)

    zip_name = project_name
    # verses
    if export_type == "verses":
        filenames = [os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_VERSES, f'{reading.ref.fmt_verse} - {cfg["author"]}.mp3') for reading in reading_list_sorted]
        zip_name = f"{cfg['book']} Reading - Verses"
    elif export_type == "chapters":
        filenames = [os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT_CHAPTERS, f'{reading.ref.fmt_chapter} - {cfg["author"]}.mp3') for reading in reading_list_sorted]
        zip_name = f"{cfg['book']} Reading - Chapters"
    else:
        filenames = [os.path.join(PROJECT_DIR, project_name, PROJECT_DIR_EXPORT, f'{reading.ref.book} - {cfg["author"]}.mp3') for reading in reading_list_sorted]
        zip_name = f"{cfg['book']} Reading"

    return reply({})
    # zip_buffer = BytesIO()
    #
    # with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    #     for filename in filenames:
    #         if os.path.isfile(filename):
    #             zip_file.write(filename, os.path.basename(filename))
    #         else:
    #             abort(400, f"File {filename} does not exist")
    #
    # # Seek to the beginning of the BytesIO buffer
    # zip_buffer.seek(0)
    #
    # return send_file(
    #     zip_buffer,
    #     mimetype='application/zip',
    #     as_attachment=True,
    #     download_name=f'{zip_name}.zip',
    # )

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
