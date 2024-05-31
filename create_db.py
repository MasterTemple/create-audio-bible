from functions import get_current_project, get_db_name
import json
import os
import re
from pymongo import MongoClient

from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE

segment_id = 0

def insert_segments_into_db(segments):
    global segment_id
    global word_id
    project_name = get_current_project()
    transcript_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR)
    # initialize
    segment_id = 0
    segment_doc = []

    # for each transcript/source
    for file in os.listdir(transcript_folder):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)
        id, _ = file.split(".")
        segment_doc.extend(create_segment_doc(data, id))

    # write to db
    segments.delete_many({})
    segments.insert_many(segment_doc)

def get_next_start(l, i):
    while 'start' not in l[i]:
        i += 1
    return l[i]['start']
def get_prev_end(l, i):
    while 'end' not in l[i]:
        i -= 1
    return l[i]['end']

def create_segment_doc(data, source_id):
    global segment_id
    arr = []
    data = data['word_segments']
    i = 1
    w = 0
    while w < len(data):
        segment_id += 1
        seg = data[w]
        content = seg['word']
        if 'start' in seg:
            start = seg['start']
        else:
            # start = data[w-1]['end']
            start = get_prev_end(data, w)
        if 'end' in seg:
            end = seg['end']
        else:
            end = get_next_start(data, w)
            # end = data[w+1]['start']
        arr.append({
            "id": segment_id,
            "source": source_id,
            "content": content,
            "start": start,
            "end": end,
            "sequence": i
        })
        i += 1
        w += 1
    return arr

def insert_searches_into_db(segments, searches):
    the_map = {}
    for seg in segments.find({}):
        word = re.sub(r"[^A-z0-9\s\-]", "", seg['content'].lower())
        try:
            the_map[word].append(seg["id"])
        except:
            the_map[word] = [seg["id"]]

    id = 1
    search_doc = []
    for k, v in the_map.items():
        search_doc.append({
            "id": id,
            "word": k,
            "segments": v,
        })
        id += 1
    searches.delete_many({})
    searches.insert_many(search_doc)

def load():
    """
    Description:
        This is the master function to call!
    """
    db_name = get_db_name()
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    searches = db["searches"]
    segments = db["segments"]
    insert_segments_into_db(segments)
    insert_searches_into_db(segments, searches)
    print("Segments:", segments.count_documents({}))
    print("Searches:", searches.count_documents({}))
