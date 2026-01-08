from fastapi import APIRouter, Response
from pathlib import Path

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent / 'static'


def _read_static(name: str) -> str:
    p = STATIC_DIR / name
    return p.read_text(encoding='utf-8')


@router.get("/")
async def index():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8' />
        <title>Machi_tan</title>
      </head>
      <body style="font-family:system-ui, -apple-system, 'Segoe UI', Roboto, 'Meiryo', sans-serif; margin:2rem">
        <h1>Machi_tan v2</h1>
        <p><a href="app?mode=teacher">先生用ページ</a> | <a href="app">生徒用ページ</a></p>
      </body>
    </html>
    """
    return Response(content=html, media_type='text/html')

