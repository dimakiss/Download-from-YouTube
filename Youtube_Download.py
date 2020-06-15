from itertools import product
import History_db
import calendar,multiprocessing,requests,os,sys,youtube_dl,time,glob,shutil
from datetime import datetime
import io
from time import sleep
import _thread
class YoutubeDownload:
    def __init__(self):
        self.set_up()
        self.didnt=[]
        os.chdir(os.getcwd() + "\\downloads_")
        self.multi_processing(self.dowload,self.urls_to_download)
        #self.clear_files()
        self.number_of_downloaded_files = self.urls_to_download.__len__()

    def set_up(self):
        self.set_download_folder()
        self.parameters()
        print("Getting the urls")
        self.urls_to_download=self.get_urls(self.months,self.watch_times)
        self.count=0
        self.total=self.urls_to_download.__len__()

    def parameters(self):
        self.number_of_files = 0
        self.number_of_processors = 8
        self.months = 1
        self.watch_times = 15
        if sys.argv.__len__() == 4:
            self.months = float(sys.argv[1])
            self.watch_times = int(sys.argv[2])
            self.number_of_processors = int(sys.argv[3])
    def set_download_folder(self):
        if os.path.isdir(os.getcwd() + '\\downloads_') == False:
            os.mkdir(os.getcwd() + "\\downloads_")

    def get_urls(self,months, number_of_views):
        history = History_db.History_db()
        data = history.data
        names = []
        url = []
        count = []
        for row in data:
            if self.is_youtube_url(row[1]) and self.is_last_visit_fit(months, row[5]):
                r = str(row[2]).split(" - YouTube")[0]
                r = self.remove_notification(r)  # if you have notification the name will look like this (number)name
                # example: (11) Test - YouTube
                if r not in names:
                    r=self.remove_notification(r)
                    r=" ".join(r.split())
                    names.append(r)
                    url.append(str(row[1]).split('&')[0])
                    count.append(0)
                count[names.index(r)] += int(row[3])
        names_temp = []
        url_temp = []
        count_temp = []
        for i in range(count.__len__()):
            if count[i] >= number_of_views:
                url_temp.append(url[i])
                names_temp.append(names[i])
                count_temp.append(count[i])

        results = self.multi_processing(self.is_music, url_temp)
        text_output = []
        url = []
        name = []
        youtube_urls = []
        for i in range(results.__len__()):
            if results[i]:
                text_output.append([names_temp[i], url_temp[i], count_temp[i]])
                url.append(url_temp[i])
                names.append(names_temp[i])
        text_output = self.sort_by_views(text_output)
        self.save_data_to_text(text_output)
        return url

    def is_youtube_url(self,url):
        return "https://www.youtube.com/watch?v=" == url[:32]

    def is_last_visit_fit(self,months, last_visit):
        if last_visit != 0:
            time = int(last_visit) // 1000000 - 11644473600
            return int(calendar.timegm(datetime.utcnow().utctimetuple())) - months * 30 * 24 * 60 * 60 <= time
        return False

    def remove_notification(self,name):
        r = str(name).split(" - YouTube")[0]
        if '(' == r[0]:
            while ')' != r[0]:
                r = r[1:]
            r = r[1:]
        return r

    def multi_processing(self,function, _product_):
        with multiprocessing.Pool(processes=self.number_of_processors) as pool:
            self.results = pool.starmap(function, product(_product_))
            pool.close()
        return self.results

    def is_music(self,url):

        # metod 1 API method

        #url = "https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id=" + url.split('watch?v=')[1] + "&key="
        #key = "YOUR API KEY HERE" #YOUR API KEY HERE
        #url += key
        #result = requests.get(url).text
        #for i in result.split('\n'):
        #    if "categoryId" in i:
        #        return "10" in i
        #return False

        # method 2 web scraping method

        result = requests.get(url).text
        if "category" not in result:
            return False
        return result.split("category")[1][5:].split(str("\\"))[0].lower()=="music"

    def sort_by_views(self,list):
        list.sort(key=lambda output: output[2], reverse=True)  # reverse by third value
        return list

    def save_data_to_text(self,data):
        text_output = "\t\t\t\t URL\t\t\t\t   Times Watched \t\t\t\t Name\n"
        for i in data:
            text_output += str(i[1]) + " " + str(i[2]) + " " +str(i[0])+ "\n"
        with io.open(os.getcwd() + "\\url_data.txt", 'w', encoding="utf-8") as f:
            f.write(text_output)
        f.close()


    def dowload(self,url):
        for i in range(30):
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'no_warnings': True,
                    'quiet': True
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return 1
            except:
                pass
        self.didnt.append(url)

    def clear_file_name(self):
        for file in glob.glob("*.mp3"):
            try:
                os.rename(file,(str(file))[:-16] + "." + (str(file)).split('.')[-1])
            except:
                pass
                #os.remove(file)


    def progress(self,count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


