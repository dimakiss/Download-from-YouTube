from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime
import os,calendar,sqlite3,timeit,requests,youtube_dl,glob,sys,multiprocessing,shutil,time
from itertools import product
from moviepy.editor import *
start = timeit.default_timer()

number_of_processors=8
def move():
    counter=0
    #for file in glob.glob("*.mp3"):
    #    try:
    #        shutil.move(file, os.path.join(os.getcwd() + "\\downloads_\\",
    #                                       (str(file))[:-16] + "." + (str(file)).split('.')[-1]))
    #        counter+=1
    #    except:
    #        os.remove(file)
    #return counter
    return glob.glob("*.mp3").__len__()
text=[]
def dowload(url):

    ydl_opts = {}
    for i in range(20):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return 1
        except:
            if i>10:
                time.sleep(1)
            pass
    text.append(url)
#def donwload(url)
    
def is_music(url):
    url="https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id="+url.split('watch?v=')[1]+"&key="
    key="AIzaSyCIFQIwDZ8CQMYiXn6BYKbUXgCvHnKAw9g"
    url+=key
    result = requests.get(url).text
    for i in result.split('\n'):
        if "categoryId" in i:
            return "10" in i
    return False

#"https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id=8dl5ZkSnQ6c&key=AIzaSyCIFQIwDZ8CQMYiXn6BYKbUXgCvHnKAw9g"


def get_urls(months,number_of_views):
    path=os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\"
    shutil.copyfile(path+"History",
             path+"History1")

    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect(path+"History1")
    c = con.cursor()
    c.execute("SELECT * FROM urls ORDER BY last_visit_time")
    data = c.fetchall()
    con.close()
    os.remove(path+"History1")

    names = []
    url = []
    count = []
    for row in data:
        if "https://www.youtube.com/watch?v=" == row[1][:32] and row[5] != 0:
            time = int(row[5]) // 1000000 - 11644473600
            if int(calendar.timegm(datetime.utcnow().utctimetuple())) - months * 30 * 24 * 60 * 60 <= time:
                r = str(row[2]).split(" - YouTube")[0]
                if ') ' in r:
                    r = r.split(') ')[1]
                if r not in names:
                    names.append(r)
                    url.append(str(row[1]).split('&')[0])
                    count.append(0)
                count[names.index(r)] += int(row[3])
    names_temp = []
    url_temp = []
    count_temp = []
    for i in range(count.__len__()):
        if count[i]>=number_of_views:
            url_temp.append(url[i])
            names_temp.append(names[i])
            count_temp.append(count[i])

    results = multi_processing(is_music, url_temp)
    text_output=[]
    url=[]
    name=[]
    for i in range(results.__len__()):
        if results[i]:
            text_output.append([names_temp[i], url_temp[i],count_temp[i]])
            url.append(url_temp[i])
            names.append(names_temp[i])
    text_output.sort(key = lambda output: output[2],reverse=True) #reverse by third value
    save_data_to_text(text_output)
    return url

def multi_processing(function,_product_):
    with multiprocessing.Pool(processes=number_of_processors) as pool:
        results = pool.starmap(function, product(_product_))
        pool.close()
    return results

def save_data_to_text(data):
    text_output="\t\t\t\t URL\t\t\t\t   Times Watched\n"
    for i in data:
        text_output+=str(i[1])+" "+str(i[2])+"\n"

    with open(os.getcwd()+"\\url_data.txt",'w') as f:
        f.write(text_output)
    f.close()

if __name__ == '__main__':
    number_of_files=0
    number_of_processors = 8
    months=4
    watch_times=10
    if sys.argv.__len__() == 4:
        months=float(sys.argv[1])
        watch_times=int(sys.argv[2])
        number_of_processors = int(sys.argv[3])
    if os.path.isdir(os.getcwd() + '\\downloads_') == False:
        os.mkdir(os.getcwd()+"\\downloads_")
    urls=get_urls(months,watch_times)
    os.chdir(os.getcwd() + "\\downloads_")
    number_of_processors=5
    multi_processing(dowload, urls)
    number_of_files=move()

    clear = lambda: os.system('cls')
    clear()
    stop = timeit.default_timer()
    print("Files downloaded: "+str(number_of_files)+"\t Took: ",int(stop - start),"s",urls.__len__(),text)

