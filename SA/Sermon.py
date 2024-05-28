from __future__ import annotations
from SA.Speaker import Speaker
from SA.Broadcaster import Broadcaster
from SA.MediaSet import MediaSet
import requests


class Sermon:
    def __init__(self):
        self.type: str = None
        self.sermonID: str = None
        self.broadcaster: Broadcaster = None
        self.speaker: Speaker = None
        self.displayTitle: str = None
        self.fullTitle: str = None
        self.subtitle: str = None
        self.preachDate: str = None  # actually date
        self.pickDate: str = None  # actually date
        self.languageCode: str = None
        self.bibleText: str = None
        self.moreInfoText: str = None
        self.eventType: str = None
        self.downloadCount: str = None
        self.media: MediaSet = None

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict):
        c = cls()
        c.type = data['type']
        c.sermonID = data['sermonID']
        c.broadcaster = Broadcaster.from_dict(data['broadcaster'])
        c.speaker = Speaker.from_dict(data['speaker'])
        c.displayTitle = data['displayTitle']
        c.fullTitle = data['fullTitle']
        c.subtitle = data['subtitle']
        c.preachDate = data['preachDate']  # actually date
        c.pickDate = data['pickDate']  # actually date
        c.languageCode = data['languageCode']
        c.bibleText = data['bibleText']
        c.moreInfoText = data['moreInfoText']
        c.eventType = data['eventType']
        c.downloadCount = data['downloadCount']
        c.media = MediaSet.from_dict(data['media'])
        return c

    def to_dict(self):
        return self.__dict__

    def download_audio(self, download_path: str):
        audio_files = self.media.audio
        if len(audio_files) == 0:
            return
        # get highest bitrate file
        file = sorted(audio_files, key=lambda f: -f.bitrate)[0]
        url = file.downloadURL

        response = requests.get(url, stream=True)
        with open(download_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024):
                fd.write(chunk)

        return download_path
