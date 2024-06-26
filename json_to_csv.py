from functions import get_current_project
import json
import os
import re
import pandas as pd

from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE

source_id = 0
segment_id = 0

def create_data_csv():
    global source_id
    global segment_id
    global word_id
    project_name = get_current_project()
    transcript_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR)
    csv_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_CSV_DIR)
    # initialize
    source_id = 0
    segment_id = 0
    sources_csv = []
    segments_csv = []

    # for each transcript/source
    for file in os.listdir(transcript_folder):
        if not file.endswith(".json"):
            continue
        print(f'"{os.path.join(transcript_folder, file)}"')
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)
        id, _ = file.split(".")
        # source csv
        source_id += 1
        # id, value
        sources_csv.append([source_id, id])
        # segment csv
        segments_csv.extend(create_segment_csv(data))

    # write to csv
    sources_df = pd.DataFrame(sources_csv)
    sources_df.to_csv(os.path.join(csv_folder, CSV_SOURCES_FILE), index=False, lineterminator="\n")
    segments_df = pd.DataFrame(segments_csv)
    segments_df.to_csv(os.path.join(csv_folder, CSV_SEGMENTS_FILE), index=False, lineterminator="\n")

def get_next_start(l, i):
    while 'start' not in l[i]:
        i += 1
    return l[i]['start']
def get_prev_end(l, i):
    while 'end' not in l[i]:
        i -= 1
    return l[i]['end']

def create_segment_csv(data):
    global source_id
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
        i += 1
        arr.append([segment_id, source_id, content,
                   start, end, i])
        w += 1
    return arr


def create_search_csv():
    global segment_id
    segment_id = 1
    # create the map
    the_map = {}
    project_name = get_current_project()
    transcript_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR)
    csv_folder = os.path.join(PROJECT_DIR, project_name, PROJECT_CSV_DIR)

    for file in os.listdir(transcript_folder):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)
        the_map = get_values(the_map, data)

    if '' in the_map:
        del the_map['']

    # convert to csv
    batch_size = 50
    the_csv = []

    for k, v in the_map.items():
        my_list = list(map(lambda x: str(x), v))
        for i in range(0, len(my_list), batch_size):
            batch = my_list[i:i+batch_size]
            s = ",".join(batch)
            the_csv.append([k, s])

    df = pd.DataFrame(the_csv)
    df.to_csv(os.path.join(csv_folder, CSV_SEARCHES_FILE), index=False, lineterminator="\n")

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
