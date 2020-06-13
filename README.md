# Download from YouTube
This script download music from youtube based on your history.\
You can input the number of months back and the number of views that this scrip will count.\
The purpose of the view count is very simple if you hear the same music **x** times means that you probably like it.

## Install Requirements
```
pip install -r requirements.txt
```

## Usage

```
python main.py <number_months> <times_watched> <processors>
```

* **number_months** - number of months you want the scrip to look back in the history

* **times_watched** - watch at least this number of times

* **processors** - this script uses parallel computation (multiprocessing) recommended 4/8 based on how strong your pc

`Note: You can run the script without these variables the default setting is number_months=1 watch_times=5 processors = 4`

The script needs to filter out all the non-music youtube videos, Which takes time.\
Especially if you watch a lot of youtube content. \
Also, every music file will need to be downloaded which depends on you download speed.\
All the music downloaded to the folder named "donwloads_" created in the path you execute the script.

Some times few files will not get downloaded due to `youtube-dl` server errors you can try running the script twice to ensure the download of all the files 
## Example

55 music files 1.17 took 590 seconds **(10 min)**
