import requests
class Url:

    def __init__(self,url,count):
        self.url=url
        self.count=count
        self.set_up()
    def set_up(self): # title(name) and is music
        self.temp_url = "https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id=" + self.url.split('watch?v=')[1] + "&key="
        self.key = "YOUR API KEY HERE"
        self.temp_url += self.key
        result = requests.get(self.temp_url).text
        for row in result.split('\n'):
            if "title" in row:
                self.name=row.split('"')[-2]
