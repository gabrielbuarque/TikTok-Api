import os
import asyncio
from fastapi import FastAPI, Query
from TikTokApi import TikTokApi, exceptions

# Precisamos instalar:
# pip install fastapi uvicorn TikTokApi httpx playwright

app = FastAPI()

# Pegar o ms_token do ambiente (definido no EasyPanel)
ms_token = os.environ.get("ms_token")

@app.on_event("startup")
async def startup_event():
    """
    Inicializa a API do TikTokApi no evento de startup do FastAPI.
    """
    global api
    api = TikTokApi()
    # Tenta criar a sessão com ms_token
    await api.create_sessions(
        ms_tokens=[ms_token],    # cookie ms_token real
        num_sessions=1,
        sleep_after=3,
        headless=False,          # Tenta não rodar em headless
        browser="webkit",        # Em vez de "chromium"
    )

@app.get("/")
def root():
    """
    Teste de status da API.
    """
    return {"message": "TikTok API running"}

@app.get("/user")
async def get_user(username: str = Query(...)):
    """
    Retorna informações de um usuário do TikTok.
    Exemplo de uso:
    GET /user?username=therock
    """
    user_obj = api.user(username=username)
    try:
        data = await user_obj.info()
        return {"username": username, "user_info": data}
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot. Tente headless=False, outro browser, proxy, etc.", "detail": str(e)}

@app.get("/user/playlists")
async def get_user_playlists(username: str = Query(...)):
    """
    Retorna playlists de um usuário e alguns vídeos de cada playlist.
    Exemplo:
    GET /user/playlists?username=therock
    """
    user_obj = api.user(username=username)
    playlists = []
    try:
        async for playlist in user_obj.playlists(count=3):
            videos_data = []
            async for vid in playlist.videos(count=3):
                videos_data.append(vid.as_dict)
            playlists.append({
                "playlist_name": playlist.name,
                "videos": videos_data
            })
        return playlists
    except exceptions.EmptyResponseException as e:
        return {"error": "Possível bloqueio do TikTok", "detail": str(e)}

@app.get("/search")
async def search_videos(query: str = Query(...)):
    """
    Busca vídeos que batem com o termo fornecido.
    Exemplo:
    GET /search?query=funny cats
    """
    results = []
    try:
        async for video in api.search.videos(query, count=10):
            results.append(video.as_dict)
        return results
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}

@app.get("/trending")
async def trending_videos():
    """
    Retorna vídeos em alta (trending).
    Exemplo:
    GET /trending
    """
    videos = []
    try:
        async for video in api.trending.videos(count=10):
            videos.append(video.as_dict)
        return videos
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}

@app.get("/hashtag")
async def hashtag_videos(tag: str = Query(...)):
    """
    Retorna vídeos de uma hashtag específica.
    Exemplo:
    GET /hashtag?tag=funny
    """
    tag_obj = api.hashtag(name=tag)
    results = []
    try:
        async for video in tag_obj.videos(count=10):
            results.append(video.as_dict)
        return results
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}

@app.get("/sound")
async def sound_videos(sound_id: str = Query(...)):
    """
    Retorna vídeos de um determinado som (sound_id).
    Exemplo:
    GET /sound?sound_id=7016547803243022337
    """
    sound = api.sound(id=sound_id)
    results = []
    try:
        async for video in sound.videos(count=10):
            results.append(video.as_dict)
        return results
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}

@app.get("/video")
async def get_video(url: str = Query(...)):
    """
    Retorna informações de um vídeo específico via URL.
    Exemplo:
    GET /video?url=https://www.tiktok.com/@username/video/123456
    """
    video_obj = api.video(url=url)
    try:
        info = await video_obj.info()
        return {"video_info": info}
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}

@app.get("/comment")
async def video_comments(video_id: str = Query(...)):
    """
    Retorna comentários de um vídeo.
    Exemplo:
    GET /comment?video_id=7248300636498890011
    """
    video = api.video(id=video_id)
    comments = []
    try:
        async for comment in video.comments(count=10):
            comments.append(comment.as_dict)
        return comments
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}
