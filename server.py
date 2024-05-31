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

import os
import sqlite3
from flask import Flask, request, send_file, jsonify
import subprocess
from io import BytesIO
from flask_cors import CORS
import json
from functions import get_project_config, get_db_name, get_current_project
from find_readings import get_esv_content
from trim import trim_file
from vars import JSON_READINGS_FILE, PROJECT_CONFIG_FILE_NAME, PROJECT_DIR, PROJECT_JSON_DIR

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

@app.route('/esv', methods=['POST'])
def esv():
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

@app.route('/readings', methods=['GET'])
def readings():
    """
    Description:
        Get the readings.json file
    Parameters:
    Returns:
        book_tree
    """
    with open(os.path.join(PROJECT_DIR, get_current_project(), PROJECT_JSON_DIR, JSON_READINGS_FILE), "r") as f:
        data = json.load(f)
    return reply(data)

@app.route('/audio', methods=['POST'])
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
    data = request.json
    output_path = trim_file(
        project_name,
        data["file_id"],
        data["start_time"],
        data["end_time"],
        data["volume"]
    )
    with open(output_path, "rb") as f:
        return f.read()

@app.route('/export', methods=['POST'])
def export():
    """
    Description:
    Parameters:
    (book_tree) -> .mp3 | .zip
    """
    pass

@app.route('/save', methods=['POST'])
def save():
    """
    Description:
    Parameters:
    (book_tree) -> None
    """
    pass

if __name__ == '__main__':
    # host server
    app.run(debug=True) # ssl_context='adhoc'