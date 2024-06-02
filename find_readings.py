import pandas as pd
import os
import re
from dataclasses import dataclass
import json
from pymongo import MongoClient
import sqlite3
from functions import get_current_project, get_db_name, get_project_config
from vars import CURRENT_PROJECT_FILE, DATA_DIR, JSON_READINGS_FILE, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_JSON_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_CSV_DIR, CSV_SEGMENTS_FILE, CSV_SOURCES_FILE, CSV_SEARCHES_FILE

searches = {}
segments = {}

def search(word):
    global searches
    if word in searches:
        return searches[word]
    else:
        return []

def print_segment_range(s, e):
    print(" ".join([segments[i]["content"] for i in range(s, e + 1)]))

@dataclass
class Reference:
    book: str
    chapter: int
    verse: int
    content: str

@dataclass
class Reading:
    id: str
    start_time: float
    end_time: float
    start_seg: int
    end_seg: int
    content: str

# get Bible verses
bible_sqlite = "ESV.sqlite"
with open("./references.json", "r") as f:
    references = json.load(f)

def get_esv_content(book: str, chapter: int, verse: int) -> str:
    con = sqlite3.connect(bible_sqlite)
    cur = con.cursor()
    res = cur.execute(
        f"SELECT content FROM '{book}' WHERE chapter={chapter} AND verse={verse} ORDER BY verse ASC;")
    element = res.fetchone()
    return element[0]

def get_esv_book(book: str) -> dict[str, str]:
    con = sqlite3.connect(bible_sqlite)
    cur = con.cursor()
    res = cur.execute(
        f"SELECT chapter, verse, content FROM '{book}' ORDER BY verse, chapter ASC;")
    elements = res.fetchall()
    reference_to_content = {f"{book} {e[0]}:{e[1]}": e[2] for e in elements}
    return reference_to_content

def get_all_verses_and_content(book) -> list[Reference]:
    refs: list[Reference] = []
    for chapter, verses_in_chapter in enumerate(references[book]):
        if chapter == 0:
            continue
        for verse in range(1, verses_in_chapter + 1):
            content = get_esv_content(book, chapter, verse)
            ref = Reference(book, chapter, verse, content)
            refs.append(ref)
    return refs

def find_readings(ref: Reference) -> list[Reading]:
    words = [
        word for word in
            re.split(r"\s",
                re.sub(r"[^A-z0-9\s\-]", "",
                    ref.content.lower()
                )#.replace("bondservant", "bond servant") # dont ask
            )
        if len(word) > 0
    ]
    word_count = len(words)
    valid_offset = 4
    accuracy = 0.6
    readings: list[Reading] = []
    for i, word in enumerate(words[:2]):
        start_word = word
        end_word = words[-1 - i]
        start_segs = search(start_word)
        end_segs = search(end_word)
        # print(start_segs)
        # print(end_segs)
        # reading_segment_ranges = [(s, s + size) for s in start_segs if s + size in end_segs]
        # segments_index = [(s, e) for s, e in zip(start_segs, end_segs) if (e - s < valid_offset) and (s > e)]
        segments_index = [(s, e) for s in start_segs for e in end_segs if (s < e) and (abs(e - s - word_count - (2*i)) < valid_offset)]
        # print(segments_index)
        for s, e in segments_index:
            valid_count = 0
            # print(s, e + 1)
            for j in range(s, e + 1):
                # print(j - s, words[j - s])
                if j - s >= word_count:
                    continue
                valid_count += 1 if segments[j]["content"] == words[j - s] else 0
            rating = (valid_count) / (e - s)
            # valid segment -> give reading
            # print(rating)
            if rating > accuracy:
                content = " ".join([segments[i]["content"] for i in range(s, e + 1)])
                readings.append(
                    Reading(
                        segments[s]["source"],
                        segments[s]["start"],
                        segments[e]["end"],
                        s,
                        e,
                        content
                    )
                )
            if len(readings) == 5:
                break
        if len(readings) > 0:
            break
    return readings



# def find_all_readings():
#     global searches
#     global segments
#     client = MongoClient('mongodb://localhost:27017/')
#     db = client[get_db_name()]
#     config = get_project_config()
#
#     searches = {s["word"]: s["segments"] for s in db["searches"].find({})}
#     segments = {s["id"]: s for s in db["segments"].find({})}
#
#     data = {}
#     book = config["book"]
#
#     for ref in get_all_verses_and_content(book):
#         full_ref = f"{ref.book} {ref.chapter}:{ref.verse}"
#         print(f"Finding '{full_ref}'", end = "")
#         data[full_ref] = [reading.__dict__ for reading in find_readings(ref)]
#         print(f" - {len(data[full_ref])} results")
#
#     project_name = get_current_project()
#     file = os.path.join(PROJECT_DIR, project_name, PROJECT_JSON_DIR, JSON_READINGS_FILE)
#     with open(file, "w") as f:
#         f.write(json.dumps(data, indent=2))
#

def raw_sequence_match(words: list[str]) -> list[Reading]:
    stack = []
    for word in words:
        occurrences = search(word)
        if len(stack) == 0:
            stack.append(occurrences)
        else:
            stack.append(
                [
                    o for o in occurrences
                    if o - 1 in stack[-1]
                ]
            )

    readings = []
    for end in stack[-1]:
        beg = end - len(words) + 1

        transcription = " ".join([segments[i]["content"] for i in range(beg, end + 1)])
        readings.append(
            Reading(
                segments[beg]["source"],
                segments[beg]["start"],
                segments[end]["end"],
                beg,
                end,
                transcription
            )
        )
    return readings

# def 

def search_sequence(content: str):
    hyphen_count = len(re.sub(r"[^\-]", "", content))
    words = [
        word for word in
            re.split(r"\s",
                re.sub(r"[^A-z0-9\s]", "",
                    # re.sub(r"['’]", "",
                    content.lower()
                    # )#.replace("bondservant", "bond servant") # dont ask
                )
            )
        if len(word) > 0
    ]

    stack = []
    for word in words:
        occurrences = search(word)
        # print(f"{word}: {len(occurrences)}")
        if len(stack) == 0:
            stack.append(occurrences)
        else:
            # stack.append([o for o in occurrences if o - 1 in stack[-1]])
            # stack.append([o for o in occurrences if o - 1 in stack[-1] or o - 2 in stack[-2]])
            # stack.append([o for o in occurrences if any([o - i in stack[-i] for i in range(max(1, len(stack) - 3), len(stack) + 1)])])
                # [o for o in occurrences if next((o - i in stack[-i] for i in range(max(1, len(stack) - 3), len(stack) + 1)), False)]
            stack.append(
                [
                    o for o in occurrences
                    if o - 1 in stack[-1]
                    # if bool(
                    #     next(
                    #         (o - 1 in stack[-i] for i in range(1, hyphen_count + 2)),
                    #          False
                    #     )
                    # )
                ]
            )

    readings = []
    for end in stack[-1]:
        beg = end - len(words) + 1

        transcription = " ".join([segments[i]["content"] for i in range(beg, end + 1)])
        readings.append(
            Reading(
                segments[beg]["source"],
                segments[beg]["start"],
                segments[end]["end"],
                beg,
                end,
                transcription
            )
        )
    return readings

def create_words(content: str) -> list[str]:
    return [
        word for word in
            re.split(r"\s", content)
        if len(word) > 0
    ]


def search_with_sequence_method(content: str) -> list[Reading]:
    word_sets = [
        # match when removing hyphen
        create_words(re.sub(r"[^A-z0-9\s]", "", content.lower())),
        # match when replacing hyphen with a space (splitting into 2 words)
        create_words(re.sub(r"[^A-z0-9\s]", "", re.sub(r"[-—]", " ", content.lower()))),
        # match using hyphen to search
        create_words(re.sub(r"[^A-z0-9\s\-]", "", content.lower())),
    ]

    # first pass with basic raw sequence matching
    for words in word_sets:
        readings = raw_sequence_match(words)
        if len(readings) > 0:
            return readings

    # split each set of words into 2 sets, see if they both can submatch and then if the end of the first and start of the second are close
    for words in word_sets:
        for i in range(3, len(words) - 2):
            # ws = word set
            ws1 = words[:i]
            ws2 = words[i:]
            # r = readings
            readings1 = raw_sequence_match(ws1)
            readings2 = raw_sequence_match(ws2)
            readings = []
            for r1 in readings1:
                for r2 in readings2:
                    if r2.start_seg - r1.end_seg < 3:
                        # if i just join them, i miss what is in between
                        transcription = " ".join([segments[i]["content"] for i in range(r1.start_seg, r2.end_seg + 1)])
                        readings.append(
                            Reading(
                                r1.id,
                                r1.start_time,
                                r2.end_time,
                                r1.start_seg,
                                r2.end_seg,
                                transcription

                            )
                        )
            if len(readings) > 0:
                return readings



    return []

def find_all_readings():
    global searches
    global segments
    client = MongoClient('mongodb://localhost:27017/')
    db = client[get_db_name()]
    config = get_project_config()

    searches = {s["word"]: s["segments"] for s in db["searches"].find({})}
    segments = {s["id"]: s for s in db["segments"].find({})}

    data = {}
    book = config["book"]

    for ref in get_all_verses_and_content(book):
        full_ref = f"{ref.book} {ref.chapter}:{ref.verse}"
        print(f"Finding '{full_ref}'", end = "")
        data[full_ref] = [reading.__dict__ for reading in search_with_sequence_method(ref.content)]
        print(f" - {len(data[full_ref])} results")

    project_name = get_current_project()
    file = os.path.join(PROJECT_DIR, project_name, PROJECT_JSON_DIR, JSON_READINGS_FILE)
    with open(file, "w") as f:
        f.write(json.dumps(data, indent=2))
