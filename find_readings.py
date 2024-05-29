import pandas as pd
import re
from dataclasses import dataclass
import json
from pymongo import MongoClient
import sqlite3

client = MongoClient('mongodb://localhost:27017/')
db = client['ephtc']
searches = db["searches"]
segments = db["segments"]
sources = db["sources"]

bible_sqlite = "ESV.sqlite"
book = "Ephesians"

with open("./references.json", "r") as f:
    references = json.load(f)

def get_esv_content(book: str, chapter: int, verse: int) -> str:
    con = sqlite3.connect(bible_sqlite)
    cur = con.cursor()
    res = cur.execute(
        f"SELECT content FROM '{book}' WHERE chapter={chapter} AND verse={verse} ORDER BY verse ASC;")
    verse = res.fetchone()
    # print(verse)
    return verse[0]

@dataclass
class Reference:
    book: str
    chapter: int
    verse: int
    content: str

def get_all_verses_and_content() -> list[Reference]:
    refs: list[Reference] = []
    for chapter, verses_in_chapter in enumerate(references[book]):
        if chapter == 0:
            continue
        for verse in range(1, verses_in_chapter + 1):
            content = get_esv_content(book, chapter, verse)
            ref = Reference(book, chapter, verse, content)
            refs.append(ref)
    return refs

def main():
    for ref in get_all_verses_and_content()[:1]:
        # ref.
        print(ref)
        words = re.sub(r"[\.'\"!\?,\-\—:;…\ufffd\u00ed]", "", ref.content.lower()).split(" ")
        size = len(words)
        # words = ref.content.lower().split(" ")
        start_word = words[0]
        end_word = words[-1]
        start = searches.find_one({
            "word": start_word
        })
        end = searches.find_one({
            "word": end_word
        })
        readings = [s for s in start["segments"] if s + size in end["segments"]]
        print(readings)
        res = segments.find_one({
            "id": readings[0]
        })
        print(res)


# word = "Paul"
# query = {
#     'content': word,
#     'source': {
#         '$in': [source['id'] for source in sources.find({}, {'id': 1})]
#     }
# }

# Execute the query and join with sources collection
# results = segments.aggregate([
#     {'$match': query},
#     {
#         '$lookup': {
#             'from': 'sources',
#             'localField': 'source',
#             'foreignField': 'id',
#             'as': 'source_details'
#         }
#     }
# ])
# for res in results:
#     print(res)

if __name__ == "__main__":
    main()
