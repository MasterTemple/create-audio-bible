from __future__ import annotations
from Media import Media


class MediaSet:
    def __init__(self):
        self.type: str = None
        self.audio: Media = None
        self.video: Media = None
        self.text: Media = None

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict):
        c = cls()
        c.type = data['type']
        c.audio = list(map(lambda d: Media.from_dict(d), data['audio']))
        c.video = list(map(lambda d: Media.from_dict(d), data['video']))
        c.text = list(map(lambda d: Media.from_dict(d), data['text']))
        return c
