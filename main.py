from fastapi import FastAPI, Query
from TikTokApi import TikTokApi
import os
import asyncio

app = FastAPI()
ms_token = os.environ.get("ms_token")

# ⚠️ Certifique-se de definir a variável de ambiente `ms_token`

@app.on_event("startup")
async def startup_event():
    global api
    api = TikTokApi()
    await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)


@app.get("/")
def root():
    return {"message": "TikTok API running"}


@app.get("/user")
async def get_user(username: str = Query(...)):
    user = api.user(username=username)
    return user.info_full()


@app.get("/user/playlists")
async def get_user_playlists(username: str = Query(...)):
    user = api.user(username=username)
    playlists = []
    async for playlist in user.playlists(count=3):
        videos = []
        async for video in playlist.videos(count=3):
            videos.append(video.as_dict)
        playlists.append({
            "playlist_name": playlist.name,
            "videos": videos
        })
    return playlists


@app.get("/search")
async def search_videos(query: str = Query(...)):
    results = []
    async for video in api.search.videos(query, count=10):
        results.append(video.as_dict)
    return results


@app.get("/video")
async def get_video(url: str = Query(...)):
    video = api.video(url=url)
    return video.info()


@app.get("/trending")
async def trending_videos():
    videos = []
    async for video in api.trending.videos(count=10):
        videos.append(video.as_dict)
    return videos


@app.get("/hashtag")
async def hashtag_videos(tag: str = Query(...)):
    tag_obj = api.hashtag(name=tag)
    results = []
    async for video in tag_obj.videos(count=10):
        results.append(video.as_dict)
    return results


@app.get("/sound")
async def sound_videos(sound_id: str = Query(...)):
    sound = api.sound(id=sound_id)
    results = []
    async for video in sound.videos(count=10):
        results.append(video.as_dict)
    return results


@app.get("/comment")
async def video_comments(video_id: str = Query(...)):
    video = api.video(id=video_id)
    comments = []
    async for comment in video.comments(count=10):
        comments.append(comment.as_dict)
    return comments
