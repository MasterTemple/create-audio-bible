from __future__ import annotations


class Broadcaster:
    def __init__(self):
        self.type: str = None
        self.broadcasterID: str = None
        self.shortName: str = None
        self.location: str = None
        self.country: str = None
        self.minister: str = None
        self.facebookUsername: str = None
        self.twitterUsername: str = None
        self.homePageURL: str = None
        self.latitude: float = None
        self.longitude: float = None
        self.imageURL: str = None
        self.albumArtURL: str = None
        self.bibleVersion: str = None
        self.aboutUs: str = None
        self.address: str = None
        self.serviceTimes: str = None
        self.serviceTimesArePreformatted: bool = None
        self.denomination: str = None
        self.canWebcast: bool = None
        self.webcastInProgress: bool = None
        self.phone: str = None
        self.listen_line_phone: str = None
        self.vacantPulpit: bool = None

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict):
        c = cls()
        c.type = data['type']
        c.broadcasterID = data['broadcasterID']
        c.shortName = data['shortName']
        c.location = data['location']
        c.country = data['country']
        c.minister = data['minister']
        c.facebookUsername = data['facebookUsername']
        c.twitterUsername = data['twitterUsername']
        c.homePageURL = data['homePageURL']
        c.latitude = data['latitude']
        c.longitude = data['longitude']
        c.imageURL = data['imageURL']
        c.albumArtURL = data['albumArtURL']
        c.bibleVersion = data['bibleVersion']
        c.aboutUs = data['aboutUs']
        c.address = data['address']
        c.serviceTimes = data['serviceTimes']
        c.serviceTimesArePreformatted = data['serviceTimesArePreformatted']
        c.denomination = data['denomination']
        c.canWebcast = data['canWebcast']
        c.webcastInProgress = data['webcastInProgress']
        c.phone = data['phone']
        # c.listen_line_phone = data['listen_line_phone']
        c.vacantPulpit = data['vacantPulpit']
        return c
