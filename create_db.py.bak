from functions import get_current_project
import json
import os
import re
import pandas as pd
import pandas as pd
from pymongo import MongoClient

from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE

segment_id = 0


client = MongoClient('mongodb://localhost:27017/')
db = client['ephtc']
searches = db["searches"]
segments = db["segments"]
sources = db["sources"]

def create_data_csv():
    global segment_id
    global word_id
    project_name = get_current_project()
    transcript_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR)
    csv_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_CSV_DIR)
    # initialize
    segment_id = 0
    source_doc = []
    segment_doc = []

    # for each transcript/source
    for file in os.listdir(transcript_folder):
        if not file.endswith(".json"):
            continue
        # print(f'"{os.path.join(transcript_folder, file)}"')
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)
        id, _ = file.split(".")
        # segment csv
        segment_doc.extend(create_segment_csv(data, id))

    # write to csv
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

def create_segment_csv(data, source_id):
    # global source_id
    global segment_id
    arr = []
    data = data['word_segments']
    # for i, seg in enumerate(data['word_segments']):
    #     segment_id += 1
    #     # id, source, content, start, end, order
    #     arr.append([segment_id, source_id, seg["word"],
    #                seg["start"], seg["end"], i])

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


def create_search_csv():
    global segment_id
    segment_id = 1
    # create the map
    the_map = {}
    project_name = get_current_project()
    transcript_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR)

    for file in os.listdir(transcript_folder):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)
        the_map = get_values(the_map, data)

    if '' in the_map:
        del the_map['']

    search_doc = []
    id = 1
    for k, v in the_map.items():
        search_doc.append({
            "id": id,
            "word": k,
            "segments": v,
        })
        id += 1
    searches.delete_many({})
    searches.insert_many(search_doc)


def get_values(the_map, data):
    global segment_id
    for segment in data['segments']:
        # remove irrelevant characters and make them lowercase
        words = list(map(lambda s: re.sub(
            r"[\.'\"!\?,\-\—:;…\ufffd\u00ed]", "", s['word'].lower()), segment['words']))
        for word in words:
            try:
                the_map[word].append(segment_id)
            except:
                the_map[word] = [segment_id]
        segment_id += 1
    return the_map

def create_search_db():
    the_map = {}
    for seg in segments.find({}):
        # word = re.sub(r"[\.'\"!\?,\-\—:;…\ufffd\u00ed]", "", seg['content'].lower())
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

# create_data_csv()
create_search_db()
print("Sources:", sources.count_documents({}))
print("Segments:", segments.count_documents({}))
print("Searches:", searches.count_documents({}))
# print("Sources:", len([e for e in sources.find({})]))
# print("Segments:", len([e for e in segments.find({})]))
# print("Searches:", len([e for e in searches.find({})]))
# print(len([e for e in sources.find({})]))
