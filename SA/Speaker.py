from __future__ import annotations


class Speaker:
    def __init__(self):
        self.type: str = None
        self.displayName: str = None
        self.sortName: str = None
        self.portraitURL: str = None
        self.albumArtURL: str = None
        self.roundedThumbnailImageURL: str = None
        self.bio: str = None
        self.mostRecentPreachDate: str = None  # actually date

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict):
        c = cls()
        c.type = data['type']
        c.displayName = data['displayName']
        c.sortName = data['sortName']
        c.portraitURL = data['portraitURL']
        c.albumArtURL = data['albumArtURL']
        c.roundedThumbnailImageURL = data['roundedThumbnailImageURL']
        c.bio = data['bio']
        c.mostRecentPreachDate = data['mostRecentPreachDate']  # actually date
        return c
