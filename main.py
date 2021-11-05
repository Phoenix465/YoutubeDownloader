from youtube_dl import YoutubeDL


YDL_OPTIONS = {
    "format": "bestaudio",
    "noplaylist": "True",
    "cachedir": "False",
    "quiet": "True"
}


def search_yt(query):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % query, download=False)[
                "entries"
            ][0]

        except Exception:
            return False

        return {"source": info["formats"][0]["url"],
                "title": info["title"],
                "thumbnail": info["thumbnail"],
                "duration": info["duration"],
                "link": f"https://www.youtube.com/watch?v={info['webpage_url_basename']}",
                "query": f'{info["title"]} - {info["uploader"]}'}

