import os
import asyncio
from fastapi import FastAPI, Query
from TikTokApi import TikTokApi, exceptions

app = FastAPI()

# Pega o ms_token e as configurações de headless e browser das variáveis de ambiente
ms_token = os.environ.get("ms_token")
# Em produção, é recomendável usar headless True; se quiser alterar, defina HEADLESS como "false"
headless = os.environ.get("HEADLESS", "true").lower() in ("true", "1", "yes")
browser_choice = os.environ.get("BROWSER", "webkit")  # pode ser "chromium", "firefox", "webkit", etc.

@app.on_event("startup")
async def startup_event():
    global api
    api = TikTokApi()
    # Cria sessões com as configurações definidas
    await api.create_sessions(
        ms_tokens=[ms_token],
        num_sessions=1,
        sleep_after=3,
        headless=headless,
        browser=browser_choice
    )

@app.get("/")
def root():
    return {"message": "TikTok API running"}

@app.get("/user")
async def get_user(username: str = Query(...)):
    """
    Retorna informações do usuário do TikTok.
    Exemplo: GET /user?username=therock
    """
    user_obj = api.user(username=username)
    try:
        data = await user_obj.info()
        return {"username": username, "user_info": data}
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot. Tente ajustar as configurações (ex.: HEADLESS, BROWSER, proxy).", "detail": str(e)}

@app.get("/user/playlists")
async def get_user_playlists(username: str = Query(...)):
    """
    Retorna as playlists do usuário e alguns vídeos de cada uma.
    Exemplo: GET /user/playlists?username=therock
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
        return {"error": "Possível bloqueio pelo TikTok", "detail": str(e)}

@app.get("/search")
async def search_videos(query: str = Query(...)):
    """
    Busca vídeos com base no termo informado.
    Exemplo: GET /search?query=funny cats
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
    Retorna vídeos em alta.
    Exemplo: GET /trending
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
    Retorna vídeos relacionados a uma hashtag.
    Exemplo: GET /hashtag?tag=funny
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
    Retorna vídeos relacionados a um som específico.
    Exemplo: GET /sound?sound_id=7016547803243022337
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
    Retorna informações de um vídeo específico.
    Exemplo: GET /video?url=https://www.tiktok.com/@username/video/123456
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
    Exemplo: GET /comment?video_id=7248300636498890011
    """
    video_obj = api.video(id=video_id)
    comments = []
    try:
        async for comment in video_obj.comments(count=10):
            comments.append(comment.as_dict)
        return comments
    except exceptions.EmptyResponseException as e:
        return {"error": "TikTok detectou bot", "detail": str(e)}
