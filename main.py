from __future__ import unicode_literals
import timeit
from moviepy.editor import *
import Youtube_Download

start = timeit.default_timer()

if __name__ == '__main__':

    yd=Youtube_Download.YoutubeDownload()

    clear = lambda: os.system('cls')
    clear()
    stop = timeit.default_timer()
    print("Files downloaded: "+str(yd.number_of_downloaded_files)+"\t Took: ",int(stop - start),"s",yd.urls_to_download.__len__(),yd.didnt)
