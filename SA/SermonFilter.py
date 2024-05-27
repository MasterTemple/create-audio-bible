class SermonFilter:
    def __init__(self):
        self.book: str = None
        self.chapter: int = None
        self.chapterEnd: int = None
        self.verse: int = None
        self.verseEnd: int = None
        self.eventType: str = None
        self.languageCode: str = None
        self.requireAudio: bool = None
        self.requireVideo: bool = None
        self.includeDrafts: bool = None
        self.includeScheduled: bool = None
        self.includePublished: bool = True
        self.series: str = None
        self.broadcasterID: str = None
        self.speakerName: str = None
        self.staffPick: bool = None
        self.year: int = None
        self.sortBy: str = None
        self.page: int = 1
        self.searchKeyword: str = None

    def to_dict(self):
        filter_dict = {}
        for key, value in self.__dict__.items():
            if value is not None:
                filter_dict[key] = value
        return filter_dict

    def __str__(self):
        return str(self.to_dict())

    def setBook(self, book: str):
        self.book = book

    def setChapter(self, chapter: int):
        self.chapter = chapter

    def setChapterEnd(self, chapterEnd: int):
        self.chapterEnd = chapterEnd

    def setVerse(self, verse: int):
        self.verse = verse

    def setVerseEnd(self, verseEnd: int):
        self.verseEnd = verseEnd

    def setEventType(self, eventType: str):
        self.eventType = eventType

    def setLanguageCode(self, languageCode: str):
        self.languageCode = languageCode

    def setRequireAudio(self, requireAudio: bool):
        self.requireAudio = requireAudio

    def setRequireVideo(self, requireVideo: bool):
        self.requireVideo = requireVideo

    def setIncludeDrafts(self, includeDrafts: bool):
        self.includeDrafts = includeDrafts

    def setIncludeScheduled(self, includeScheduled: bool):
        self.includeScheduled = includeScheduled

    def setIncludePublished(self, includePublished: bool):
        self.includePublished = includePublished

    def setSeries(self, series: str):
        self.series = series

    def setBroadcasterID(self, broadcasterID: str):
        self.broadcasterID = broadcasterID

    def setSpeakerName(self, speakerName: str):
        self.speakerName = speakerName

    def setStaffPick(self, staffPick: bool):
        self.staffPick = staffPick

    def setYear(self, year: int):
        self.year = year

    def setSortBy(self, sortBy: str):
        self.sortBy = sortBy

    def setPage(self, page: int):
        self.page = page

    def setSearchKeyword(self, searchKeyword: str):
        self.searchKeyword = searchKeyword



if __name__ == '__main__':
    f = SermonFilter()
    f.book = 'jhn'
    f.chapter = 3
    f.requireAudio = True

    filter_dict = f.to_dict()
    print(f)
