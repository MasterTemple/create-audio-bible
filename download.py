import os
import requests
import re
import json
from pytube import Playlist
from pytube import YouTube
from SA.SermonAudio import SermonAudioAPI
import json
from SA.Sermon import Sermon
from functions import get_current_project

from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR

def download_project_files(project_name) -> None:
    with open(os.path.join(PROJECT_DIR, project_name, PROJECT_CONFIG_FILE_NAME), "r") as f:
            config = json.loads(f.read())
    sources = config["sources"]
    for source in sources:
        download_file(source)

def download_file(source):
    # YouTube Playlist
    if bool(re.search("https://www.youtube.com/playlist", source)):
        # id = re.search("https://www.youtube.com/playlist?list=([A-z0-9]+)", source)[1]
        download_playlist(source)
    # YouTube Links
    elif bool(re.search("https://www.youtube.com/watch", source)):
        # id = re.search("https://www.youtube.com/watch?v=([A-z0-9]+)", source)[1]
        download_youtube_video_as_mp3(source)
    # SermonAudio Series
    elif bool(re.search("https://beta.sermonaudio.com/series/", source)):
        id = re.search(r"https://beta.sermonaudio.com/series/(\d+)", source)[1]
        download_sermon_audio_series(id)
    # SermonAudio Links
    elif bool(re.search("https://beta.sermonaudio.com/sermons/", source)):
        id = re.search(r"https://beta.sermonaudio.com/sermons/(\d+)", source)[1]
        download_sermon_audio_file(id)
    else:
        id = re.search(r"([A-z0-9]+)\.mp3$", source)[1]
        print(f"Downloading Audio '{source}' [{id}]")
        download_from_url(source, id)
        # print(f"Invalid URL: {source}")
        # exit(1)

def download_from_url(url, id):
    project_name = get_current_project()
    response = requests.get(url, stream=True)
    with open(os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f"{id}.mp3"), 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)

def download_sermon_audio_series(id):
    sa = SermonAudioAPI()
    sa.params.setSeries(id)
    all_sermons: list[Sermon] = []
    page = 1
    keep_going = True
    while keep_going:
        sa.params.setPage(page)
        sermons: list[Sermon] = sa.get_sermons()
        # print(sermons)
        all_sermons.extend(sermons)
        page += 1
        if len(sermons) == 0:
            break
    # print(all_sermons)
    current_project = get_current_project()
    for sermon in all_sermons:
        new_file = os.path.join(PROJECT_DIR, current_project, PROJECT_DOWNLOADS_DIR, f"{sermon.sermonID}.mp3")
        if not os.path.exists(new_file):
            print(f"Downloading Sermon '{sermon.fullTitle}' [{sermon.sermonID}]")
            sermon.download_audio(new_file)

def download_sermon_audio_file(id):
    sa = SermonAudioAPI()
    sermon: Sermon = sa.get_sermon(id)
    current_project = get_current_project()
    new_file = os.path.join(PROJECT_DIR, current_project, PROJECT_DOWNLOADS_DIR, f"{sermon.sermonID}.mp3")
    if not os.path.exists(new_file):
        print(f"Downloading Sermon '{sermon.fullTitle}' [{sermon.sermonID}]")
        sermon.download_audio(new_file)

def download_youtube_video_as_mp3(url):
    id = re.search("https://www.youtube.com/watch?v=([A-z0-9]+)", url)[1]
    print(f"Downloading YouTube Video '{url}'")
    current_project = get_current_project()
    new_file = os.path.join(PROJECT_DIR, current_project, PROJECT_DOWNLOADS_DIR, f"{id}.mp3")
    if os.path.exists(new_file):
        return
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    out_file = audio.download(output_path=os.path.join(PROJECT_DIR, current_project, PROJECT_DOWNLOADS_DIR))
    _, ext = os.path.splitext(out_file)
    if ext == ".mp3":
        new_file = id + '.mp3'
        os.rename(out_file, new_file)
    else:
        new_file = id + ext
        os.rename(out_file, os.path.join(PROJECT_DIR, current_project, PROJECT_TEMP_DOWNLOADS_DIR))
        print("Downloaded a non .mp3 file!")

def download_playlist(url):
    pl = Playlist(url)

    for video_url in pl.video_urls:
        download_youtube_video_as_mp3(video_url)
