from fastapi import FastAPI, Query
from TikTokApi import TikTokApi

app = FastAPI()
api = TikTokApi()

@app.get("/")
def read_root():
    return {"message": "TikTok API is running"}

@app.get("/user")
def get_user(username: str = Query(...)):
    user = api.user(username=username)
    return {"username": username, "user_info": user.info_full()}
