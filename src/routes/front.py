from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=['front'])


@router.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@router.get("/chat", response_class=HTMLResponse, description="Chat Page")
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
