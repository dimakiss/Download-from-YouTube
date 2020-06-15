from __future__ import unicode_literals
import timeit
from moviepy.editor import *
from time import sleep

import Youtube_Download

start = timeit.default_timer()

if __name__ == '__main__':

    yd=Youtube_Download.YoutubeDownload()
    sleep(1)
    clear = lambda: os.system('cls')
    clear()
    stop = timeit.default_timer()
    print("Files downloaded: "+str(yd.count)+"/"+str(yd.total)+"\t Took: ",int(stop - start),"s\nFaild:",yd.didnt.__len__())
