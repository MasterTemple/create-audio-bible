from SermonFilter import SermonFilter
from Sermon import Sermon
from Broadcaster import Broadcaster
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
SA_API_KEY = os.environ.get("SA_API_KEY")



class SermonAudioAPI:

    BASE_URL = 'https://api.sermonaudio.com/v2/node'

    # def __init__(self, filters: SermonFilter):
    def __init__(self):
        self.params: SermonFilter = SermonFilter()

    def get(self, endpoint: str):
        url = self.BASE_URL + endpoint
        headers = {
            "X-Api-Key": SA_API_KEY
        }
        response = requests.get(url, params=self.params.to_dict(), headers=headers)
        return response.json()

    def get_sermons(self) -> list[Sermon]:
        j: list[dict] = self.get("/sermons/")
        j = j['results']
        sermons: list[Sermon] = list(map(lambda s: Sermon.from_dict(s), j))
        return sermons

    def get_sermon(self, sermon_id) -> Sermon:
        j = self.get(f"/sermons/{sermon_id}")
        sermon = Sermon.from_dict(j)
        return sermon

    def get_broadcaster(self, broadcaster_id) -> Sermon:
        j = self.get(f"/broadcasters/{broadcaster_id}")
        broadcaster = Broadcaster.from_dict(j)
        return broadcaster
