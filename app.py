from datetime import datetime, timezone
import json
from bson import ObjectId
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from src.data_fetching.chaneel_fetch import Yotube_Data_Fetching
from src.utils.commons import youtube, convert_objectid_to_str
import uvicorn

app = FastAPI()

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="UI"), name="static")

@app.get("/channel-id")
async def channle_id(channel_url: str):
    data_fetcher = Yotube_Data_Fetching()  # Create an instance of the class
    channel_id = data_fetcher.get_channel_id_from_video_url(youtube, channel_url)  # Call the instance method
    return JSONResponse(status_code=200, content={"channel_id": channel_id})  # Return the response

@app.get("/")
async def get_home_page():
    return FileResponse("UI/index.html")


@app.get("/")
async def get_home_page():
    return FileResponse("UI/index.html")

@app.get("/Channel-Stats-data")
async def chanlle_stat_data(channel_id: str, date: datetime):
    data_fetcher = Yotube_Data_Fetching()  # Create an instance of the class
    stats_data = data_fetcher.get_channel_statistics(channel_id, date)  # Call the instance method
    if stats_data:
        existing_channel = convert_objectid_to_str(stats_data)
        return JSONResponse(status_code=200, content=existing_channel)  # Return the response


