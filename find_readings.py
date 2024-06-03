from functools import lru_cache
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

@lru_cache()
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


def raw_sequence_match_segs(words: list[str]) -> list[tuple[int, int]]:
    stack = []
    for word in words:
        occurrences = search(word)
        if len(stack) == 0:
            # if len(start_segs) == 0:
            stack.append(occurrences)
            # else:
            #     stack.append([o for o in occurrences if o not in start_segs])
        else:
            stack.append(
                [
                    o for o in occurrences
                    # if o - 1 in stack[-1]
                    if bsi(o - 1, stack[-1])
                ]
            )

    word_count = len(words)
    return [(end - word_count + 1, end) for end in stack[-1]]

def raw_sequence_match(words: list[str]) -> list[Reading]:
    stack = []
    for word in words:
        occurrences = search(word)
        if len(stack) == 0:
            # if len(start_segs) == 0:
            stack.append(occurrences)
            # else:
            #     stack.append([o for o in occurrences if o not in start_segs])
        else:
            stack.append(
                [
                    o for o in occurrences
                    # if o - 1 in stack[-1]
                    if bsi(o - 1, stack[-1])
                ]
            )

    readings = []
    for end in stack[-1]:
        beg = end - len(words) + 1
        # if beg in start_segs:
        #     continue

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

@lru_cache()
def create_words(content: str) -> list[str]:
    return [
        word for word in
            re.split(r"\s", content)
        if len(word) > 0
    ]

def binary_search_near_reading(arr: list[Reading], x: int, threshold: int) -> Reading:
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if abs(x - arr[mid].end_seg) < threshold:
            return arr[mid]
        # If x is greater, ignore left half
        elif arr[mid].end_seg < x:
            low = mid + 1
        # If x is smaller, ignore right half
        elif arr[mid].end_seg > x:
            high = mid - 1
        # means x is present at mid
        else:
            return arr[mid]
    # If we reach here, then the element was not present
    return -1

def binary_search_near(arr: list[tuple[int, int]], x: int, threshold: int) -> int:
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if abs(x - arr[mid][1]) < threshold:
            return arr[mid][1]
        # If x is greater, ignore left half
        elif arr[mid][1] < x:
            low = mid + 1
        # If x is smaller, ignore right half
        elif arr[mid][1] > x:
            high = mid - 1
        # means x is present at mid
        else:
            return arr[mid][1]
    # If we reach here, then the element was not present
    return -1

# binary search in
def bsi(x: int, arr: list[int]) -> bool:
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return True
    return False

# binary search match
def bsm(segs1: list[tuple[int, int]], segs2: list[tuple[int, int]], word_count: int, threshold: int) -> list[tuple[int, int]]:
    # narr1 = []
    # narr2 = []
    pairs = []
    # begin and end
    for b1, e1 in segs1:
        e2 = binary_search_near(segs2, b1 + word_count, threshold)
        if e2 != -1:
            # narr1.append(a1)
            # narr2.append(a2)
            pairs.append((b1, e2))
    return pairs
    # return narr1, narr2


def bsmr(arr1: list[Reading], arr2: list[Reading], word_count: int, threshold: int) -> tuple[list[Reading], list[Reading]]:
    narr1 = []
    narr2 = []
    for a1 in arr1:
        a2 = binary_search_near_reading(arr2, a1.start_seg + word_count, threshold)
        if a2 != -1:
            narr1.append(a1)
            narr2.append(a2)
    return narr1, narr2

def search_with_sequence_method(content: str, ultra_search: bool = True) -> list[Reading]:
    word_strs = [
        # match when removing hyphen
        # create_words(re.sub(r"[^A-z0-9\s]", "", content.lower())),
        re.sub(r"[^A-z0-9\s]", "", content.lower()),
        # match when replacing hyphen with a space (splitting into 2 words)
        # create_words(re.sub(r"[^A-z0-9\s]", "", re.sub(r"[-—]", " ", content.lower()))),
        re.sub(r"[^A-z0-9\s]", "", re.sub(r"[-—]", " ", content.lower())),
        # match using hyphen to search
        # create_words(re.sub(r"[^A-z0-9\s\-]", "", content.lower())),
        re.sub(r"[^A-z0-9\s\-]", "", content.lower()),
    ]

    word_sets = [create_words(word_str) for word_str in list(set(word_strs))]

    all_readings = []
    start_segs = set()

    # # first pass with basic raw sequence matching
    # for words in word_sets:
    #     # readings = raw_sequence_match(words, start_segs)
    #     readings = cached_raw_sequence_match(words)
    #     if ultra_search:
    #         for r in readings:
    #             if r.start_seg not in start_segs:
    #                 start_segs.add(r.start_seg)
    #                 all_readings.append(r)
    #     elif len(readings) > 0:
    #         return readings

    # split each set of words into 2 sets, see if they both can submatch and then if the end of the first and start of the second are close
    # for words in word_sets:
    for w, words in enumerate(word_sets):
        # sometimes they result in the same thing -> dont search again :)))))
        if w > 0 and words == word_sets[w-1]:
            continue
        word_count = len(words)
        # words = create_words(content)
        for i in range(3, word_count - 2):
            # ws = word set
            ws1 = words[:i-1]
            ws2 = words[1+i:]
            segs1 = raw_sequence_match_segs(ws1)
            segs2 = raw_sequence_match_segs(ws2)
            threshold = 4
            seg_pairs = bsm(segs1, segs2, word_count, threshold)
            # readings = []
            for start_seg_id, end_seg_id in seg_pairs:
                if start_seg_id in start_segs:
                    continue
                transcription = " ".join([segments[i]["content"] for i in range(start_seg_id, end_seg_id)])
                start_seg = segments[start_seg_id]
                end_seg = segments[end_seg_id]
                # print(f"{start_seg_id=}")
                # print(f"{start_seg=}")
                # print(f"{end_seg_id=}")
                # print(f"{end_seg=}")
                r = Reading(
                    start_seg["source"],
                    start_seg["start"],
                    end_seg["end"],
                    start_seg_id,
                    end_seg_id,
                    transcription
                )
                start_segs.add(start_seg_id)
                all_readings.append(r)
    return all_readings

def find_all_readings(ultra_search=True):
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
        # if full_ref != "1 Peter 4:4":
        #     continue
        print(f"Finding '{full_ref}'", end = "")
        data[full_ref] = [reading.__dict__ for reading in search_with_sequence_method(ref.content, ultra_search)]
        print(f" - {len(data[full_ref])} results")

    project_name = get_current_project()
    file = os.path.join(PROJECT_DIR, project_name, PROJECT_JSON_DIR, JSON_READINGS_FILE)
    with open(file, "w") as f:
        f.write(json.dumps(data, indent=2))

if __name__ == "__main__":
    find_all_readings(True)
