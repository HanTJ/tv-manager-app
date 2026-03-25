from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from datetime import datetime
import os
import subprocess
import re

from database import setup_database, get_channels, get_filtered_guide, get_now_playing, get_latest_failed_job
from scheduler import start_scheduler

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 초기 설정 및 DB 준비
setup_database()

# 백그라운드 스케줄러 시작
scheduler = start_scheduler()

def format_title_with_tags(title: str):
    tag_map = {
        "LIVE": '<span class="tag tag-live">LIVE</span>',
        "HD": '<span class="tag tag-hd">HD</span>',
        "자막": '<span class="tag tag-sub">자막</span>',
        "재방": '<span class="tag tag-rebroad">재방</span>'
    }
    formatted_title = title
    for text, html in tag_map.items():
        formatted_title = formatted_title.replace(text, html)
    return formatted_title

templates.env.filters["format_tags"] = format_title_with_tags

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, date: str = Query(None)):
    now = datetime.now()
    # 파라미터로 날짜가 들어오면 해당 날짜 사용, 없으면 오늘 날짜 사용
    current_date = date if date else now.strftime("%Y_%m_%d")
    current_time = now.strftime("%H:%M")
    
    now_playing = get_now_playing(current_date, current_time)
    
    # 최근 실패한 작업이 있는지 확인
    failed_job = get_latest_failed_job()
    
    return templates.TemplateResponse(
        request=request, name="index.html", context={
            "now_playing": now_playing,
            "current_date": current_date,
            "current_time": current_time,
            "failed_job": failed_job
        }
    )

@app.get("/list", response_class=HTMLResponse)
async def read_list(request: Request, date: str = Query(None), channel: str = None, category: str = None):
    if date is None:
        date = datetime.now().strftime("%Y_%m_%d")
        
    channels = get_channels()
    guides = get_filtered_guide(date=date, channel=channel, category=category)
    
    return templates.TemplateResponse(
        request=request, name="list.html", context={
            "channels": channels,
            "guides": guides,
            "selected_date": date,
            "selected_channel": channel,
            "selected_category": category
        }
    )

@app.post("/scrape")
async def run_scrape(date: str = Form(...), category: str = Form(...)):
    try:
        subprocess.run(["uv", "run", "main.py", date, category], check=True)
        return RedirectResponse(url=f"/list?date={date}", status_code=303)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
