from __future__ import annotations


class Media:
    def __init__(self):
        self.type: str = None
        self.mediaType: str = None
        self.live: bool = None
        self.streamURL: str = None
        self.downloadURL: str = None
        self.bitrate: int = None
        self.duration: int = None
        self.audioCodec: str = None
        self.videoCodec: str = None
        self.thumbnailImageURL: str = None

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict):
        c = cls()
        c.type = data['type']
        c.mediaType = data['mediaType']
        c.live = data['live']
        c.streamURL = data['streamURL']
        c.downloadURL = data['downloadURL']
        c.bitrate = data['bitrate']
        c.duration = data['duration']
        c.audioCodec = data['audioCodec']
        c.videoCodec = data['videoCodec']
        c.thumbnailImageURL = data['thumbnailImageURL']
        return c
