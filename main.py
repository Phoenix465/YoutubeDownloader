import os
import subprocess
import threading
import tkinter.ttk
import urllib.request
from time import time

from youtube_dl import YoutubeDL

YDL_OPTIONS = {
    "format": "best",
    "audio-format": "mp3",
    "noplaylist": "True",
    "cachedir": "False",
    "quiet": "True",
}


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def search_yt(query):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info('ytsearch:%s' % query, download=False, )[
                "entries"
            ]

            info = info[0]

        except Exception as e:
            print(f"Error: {e}")
            return False

        return {"source": info["formats"][0]["url"],
                "title": info["title"],
                "thumbnail": info["thumbnail"],
                "duration": info["duration"],
                "link": info["webpage_url"],
                "uploader": info["channel"],
                "query": f'{info["title"]} - {info["channel"]}'}


# print(search_yt("fruits basket pleasure warm up"))
# print(search_yt("https://www.youtube.com/watch?v=1coWEhuddkY"))


window = tkinter.Tk()
window.wm_title("Youtube Downloader")

icon = tkinter.PhotoImage(file=resource_path("./icon.png"))
window.iconphoto(False, icon)
window.geometry("800x300")

canvas = tkinter.Canvas(window, width=800, height=300)
canvas.pack(anchor="w")

youtubeQueryText = tkinter.Label(window, text="Youtube Query: ")
canvasYoutubeQueryText = canvas.create_window(0, 15, window=youtubeQueryText, anchor="w")

youtubeQueryEntry = tkinter.Entry(window, width=115)
canvasYoutubeQueryEntry = canvas.create_window(90, 15, window=youtubeQueryEntry, anchor="w")

searchStatusText = tkinter.StringVar()
searchStatusText.set("Status: Idle")
searchStatus = tkinter.Label(window, textvariable=searchStatusText)
canvasSearchStatus = canvas.create_window(0, 75, window=searchStatus, anchor="w")

entryWidth = 120

videoNameText = tkinter.StringVar()
videoNameText.set("Title: ")
videoName = tkinter.Entry(window, textvariable=videoNameText, width=entryWidth)
videoName.configure(state="readonly")
canvasVideoName = canvas.create_window(0, 95, window=videoName, anchor="w")

channelNameText = tkinter.StringVar()
channelNameText.set("Channel: ")
channelName = tkinter.Entry(window, textvariable=channelNameText, width=entryWidth)
channelName.configure(state="readonly")
canvasChannelName = canvas.create_window(0, 115, window=channelName, anchor="w")

linkUrlText = tkinter.StringVar()
linkUrlText.set("Link: ")
linkUrl = tkinter.Entry(window, textvariable=linkUrlText, width=entryWidth)
linkUrl.configure(state="readonly")
canvasLinkUrl = canvas.create_window(0, 135, window=linkUrl, anchor="w")

progressBar = tkinter.ttk.Progressbar(window, orient=tkinter.HORIZONTAL, length=780, mode='determinate')
canvasProgress = canvas.create_window(10, 210, window=progressBar, anchor="w")

downloadProgressText = tkinter.StringVar()
downloadProgressText.set("Download Progress: ")
downloadProgress = tkinter.Entry(window, textvariable=downloadProgressText, width=entryWidth)
downloadProgress.configure(state="readonly")
canvasDownloadProgress = canvas.create_window(0, 240, window=downloadProgress, anchor="w")

downloadTimeText = tkinter.StringVar()
downloadTimeText.set("Download Time: ")
downloadTime = tkinter.Entry(window, textvariable=downloadTimeText, width=entryWidth)
downloadTime.configure(state="readonly")
canvasDownloadTime = canvas.create_window(0, 260, window=downloadTime, anchor="w")

"""convertTimeText = tkinter.StringVar()
convertTimeText.set("Convert Time: ")
convertTime = tkinter.Entry(window, textvariable=convertTimeText, width=entryWidth)
convertTime.configure(state="readonly")
canvasConvertTime = canvas.create_window(0, 280, window=convertTime, anchor="w")"""

downloadSourceURL = tkinter.StringVar()
downloadSourceURL.set("")

audioExtensions = ["mp3", "m4a", "aac", "wav", "weba"]


audioExtensionOptionText = tkinter.StringVar()
audioExtensionOptionText.set(audioExtensions[0])

audioOptionMenu = tkinter.OptionMenu(window, audioExtensionOptionText, *audioExtensions)
canvasAudioOptionMenu = canvas.create_window(700, 175, window=audioOptionMenu, anchor="w")


def downloadClicked(button):
    def downloadThread(button):
        button.configure(state="disabled")

        url = downloadSourceURL.get()
        audioExtension = audioExtensionOptionText.get()

        try:
            u = urllib.request.urlopen(url)

        except:
            button.configure(state="normal")
            downloadProgressText.set("Failed to fetch link, please re-search")

            return

        f = open("temp.weba", 'wb')

        meta = u.info()
        fileSize = int(meta["Content-Length"])

        fileDownloadSizeCurrent = 0
        blockSize = 1024 * 32

        s = time()

        while True:
            window.update_idletasks()

            buffer = u.read(blockSize)

            if not buffer:
                break

            fileDownloadSizeCurrent += len(buffer)
            f.write(buffer)

            percentage = min(100, fileDownloadSizeCurrent / fileSize * 100)
            progressBar["value"] = round(percentage)
            downloadProgressText.set(f"Download Progress: {fileDownloadSizeCurrent}/{fileSize} - {round(percentage, 2)}%")

            e = time() - s
            downloadTimeText.set(f"Download Time: {round(e)}s")

        e = time() - s
        downloadTimeText.set(f"Download Time: {round(e, 2)}s")

        downloadProgressText.set("Converting File... (This may take a while)")
        window.update_idletasks()

        illegal = r'<>:"/\|?*%^'
        nameFilter = "".join([char for char in videoNameText.get()[6:] if char not in illegal])

        completedCommand = subprocess.run(["powershell", "-Command", f'ffmpeg -i "temp.weba" "{nameFilter}.{audioExtension}" '], capture_output=True)
        if completedCommand.returncode != 0:
            downloadProgressText.set("Error Occurred Whilst Converting File, Please Try Again")
        else:
            downloadProgressText.set("File Converted")

        button.configure(state="normal")

    downloadThread = threading.Thread(target=downloadThread, daemon=True, args=(button,))
    downloadThread.start()


downloadButton = tkinter.Button(window, text="Download", width=95, command=lambda: downloadClicked(downloadButton))
canvasDownloadButton = canvas.create_window(350, 175, window=downloadButton)
downloadButton.configure(state="disabled")


def searchClicked():
    youtubeQueryText = youtubeQueryEntry.get()

    if youtubeQueryText:
        searchStatusText.set("Status: Searching...")
        window.update_idletasks()

        songData = search_yt(youtubeQueryText)
        searchStatusText.set(f"Status: {'Finished' if songData else 'ERROR'}")

        if songData:
            downloadButton.configure(state="normal")

            videoNameText.set(f"Name: {songData['title']}")
            channelNameText.set(f"Channel: {songData['uploader']}")
            linkUrlText.set(f"Link: {songData['link']}")

            downloadSourceURL.set(songData["source"])
        else:
            downloadButton.configure(state="disabled")

            videoNameText.set(f"Name: ")
            channelNameText.set(f"Channel: ")
            linkUrlText.set(f"Link: ")

            downloadSourceURL.set("")


searchButton = tkinter.Button(window, text="Search", width=110, command=searchClicked)
canvasSearchButton = canvas.create_window(400, 45, window=searchButton)

# Image Size Scaled: 1280x720 / 2 = 640x360 or 320x180


window.mainloop()
