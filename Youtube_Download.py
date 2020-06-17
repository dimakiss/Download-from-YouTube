import History_db

from itertools import product
from datetime import datetime
from time import sleep
import calendar,multiprocessing,requests,os,sys,youtube_dl,glob,_thread,io,timeit

class YoutubeDownload:

    def __init__(self):
        start = timeit.default_timer()
        self.set_up()
        os.chdir(os.getcwd() + "\\downloads_")
        print(" Found:",self.total_mp3_count)

        t=_thread.start_new_thread(self.progress_bar_updater,())
        self.multi_processing(self.dowload,self.urls_to_download)
        self.finish=True
        self.clear_file_name()

        sleep(1)
        stop = timeit.default_timer()
        print("\n\nFiles downloaded: " + str(self.mp3_count) + "/" + str(self.total_mp3_count) + "\t Took: ",
              int(stop - start), "s\nFaild:", self.total_mp3_count - self.mp3_count)

    def set_up(self):
        self.t1=0 # parameter for progressbar

        self.set_download_folder()
        self.parameters()
        clear = lambda: os.system('cls')
        clear()
        print("Getting the urls ",end="")
        self.urls_to_download=self.get_urls()
        self.mp3_count=0
        self.total_mp3_count=self.urls_to_download.__len__()

    def parameters(self):

        # set months,watch_times,number_of_processors
        # months: take history data at the latest
        # watch_times: the minimum time that song had to be played
        # number_of_processors: number of simultaneously process
        #                       because this script uses multiprocessing

        if sys.argv==4:
            try:
                self.months = float(sys.argv[1])
                self.watch_times = max(int(sys.argv[2]),1)
                self.number_of_processors = max(int(sys.argv[3]),1)
            except:
                # default
                self.number_of_processors = 4
                self.months = 1
                self.watch_times = 5
        else:
            self.number_of_processors = 4
            self.months = 1
            self.watch_times = 5

    def set_download_folder(self):

        # ceate folder named downloads_ if needed

        if os.path.isdir(os.getcwd() + '\\downloads_') == False:
            os.mkdir(os.getcwd() + "\\downloads_")

    def get_urls(self):

        # get all urls to donload, music urls that fit to the number of watches in the right period of time (months)

        history = History_db.History_db()
        data = history.data
        names,url,count = [],[],[]
        names,url,count=self.collect_urls_by_parameters_from_data(data, names, url, count)
        names,url,count=self.filter_by_count(names,url,count)
        results = self.multi_processing(self.is_music, url)
        names, url, count = self.filter_by_is_music(names, url, count,results)
        self.generate_text_data_file(names, url, count)
        return url

    def collect_urls_by_parameters_from_data(self, data, names, url, count):
        for row in data:
            if self.is_youtube_url(row[1]) and self.is_last_visit_fit(row[5]):
                r = str(row[2]).split(" - YouTube")[0]
                r = self.remove_notification(r)  # if you have notification the name will look like this (number)name
                # example: (11) Test - YouTube
                if r not in names:
                    r = " ".join(r.split())  # remove the space at the start
                    names.append(r)
                    url.append(str(row[1]).split('&')[0])
                    count.append(0)
                count[names.index(r)] += int(row[3])
        return names,url,count

    def filter_by_count(self,names,url,count):

        # filter all urls parameters(name,url,count) by count

        names_temp = []
        url_temp = []
        count_temp = []
        for i in range(count.__len__()):
            if count[i] >= self.watch_times:
                url_temp.append(url[i])
                names_temp.append(names[i])
                count_temp.append(count[i])
        return names_temp,url_temp,count_temp

    def filter_by_is_music(self,names, url, count, results):
        names_temp = []
        url_temp = []
        count_temp = []
        for i in range(results.__len__()):
            if results[i]:
                names_temp.append(names[i])
                url_temp.append(url[i])
                count_temp.append(count[i])
        return names_temp,url_temp,count_temp

    def generate_text_data_file(self, names, url, count):

        # saves all data the pit to all the criterions which will be downloaded

        text_output = []
        for i in range(url.__len__()):
            text_output.append([names[i], url[i], count[i]])
        text_output = self.sort_lst_by_last_var(text_output)
        self.save_data_to_text(text_output)

    def is_youtube_url(self,url):

        # checks if url starts with "https://www.youtube.com/watch?v="
        #return "https://www.youtube.com/watch?v=" == url[:32]
        return url.startswith("https://www.youtube.com/watch?v=")

    def is_last_visit_fit(self, last_visit):

        # is last visit fit to the input month user

        if last_visit != 0:
            time = int(last_visit) // 1000000 - 11644473600
            return int(calendar.timegm(datetime.utcnow().utctimetuple())) - self.months * 30 * 24 * 60 * 60 <= time
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

    def sort_lst_by_last_var(self, lst):

        lst.sort(key=lambda output: output[-1], reverse=True)  # reverse by third value
        return lst

    def save_data_to_text(self, text_for_file_save):

        # save urls data to "url_data.txt"

        text_output = "\t\t URL\t\t\tTimes Watched \t Name\n\n"
        for Line in text_for_file_save:
            text_output += str(Line[1]) + "    " + str(Line[2]) + "\t" + str(Line[0]) + "\n"
        with io.open(os.getcwd() + "\\url_data.txt", 'w', encoding="utf-8") as f:
            f.write(text_output)
        f.close()

    def progress_bar_updater(self):
        not_mp3=1
        max_to_print=0
        sleep(5)
        self.finish=False
        while (not_mp3!=0 or self.mp3_count!=self.total_mp3_count) and not self.finish:
            sleep(0.5)
            self.mp3_count=glob.glob("*.mp3").__len__()
            not_mp3=glob.glob("*").__len__()-self.mp3_count
            max_to_print=max(self.mp3_count-not_mp3,max_to_print)
            self.progress(max_to_print, self.total_mp3_count)

    def dowload(self,url):

        # download url in format of mp3

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

                # For the progress bar
                clear = lambda: os.system('cls')
                clear()
                sleep(0.5)
                clear()
                #sys.stdout.flush()
                #

                pass

    def clear_file_name(self):

        # clear the "id" from the file name

        for file in glob.glob("*.mp3"):
            try:
                os.rename(file,(str(file))[:-16] + "." + (str(file)).split('.')[-1])
            except:
                pass
                #os.remove(file)

    def progress(self,count, total, status=''):

        # print progress bar in console
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        self.t1+=1
        self.t1%=4
        t2="."*self.t1+" "*(4-self.t1)
        percents = round(100.0 * count / float(total), 1)
        #bar = '=' * filled_len + '-' * (bar_len - filled_len) second option [===----]
        bar = '█' * filled_len + ' ' * (bar_len - filled_len)
        sys.stdout.write('Downloading: [%s] %s%s %s%s\r' % (bar, percents, '%', status,t2))
        sys.stdout.flush()

