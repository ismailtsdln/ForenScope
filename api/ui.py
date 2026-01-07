from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="reporting/templates")

@router.get("/ui", response_class=HTMLResponse)
async def get_ui(request: Request):
    # Simple dashboard listing generated reports
    reports_dir = "reports"
    reports = []
    if os.path.exists(reports_dir):
        reports = [f for f in os.listdir(reports_dir) if f.endswith(".html")]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "reports": sorted(reports, reverse=True),
        "title": "ForenScope Evidence Browser"
    })

@router.get("/ui/recovered")
async def list_recovered(request: Request):
    # List carved/recovered files
    recovered_dir = "recovered"
    files = []
    if os.path.exists(recovered_dir):
        files = os.listdir(recovered_dir)
    
    return templates.TemplateResponse("recovered.html", {
        "request": request,
        "files": files,
        "title": "Recovered Evidence"
    })
