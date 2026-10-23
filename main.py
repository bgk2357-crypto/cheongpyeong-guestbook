"""Day1~Day8에서 배운 함수·조건문·FastAPI로 만드는 청평의 방명록."""

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, RedirectResponse, Response

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "guestbook.db"
PAGE_SIZE = 20
MAX_ENTRIES = 1000
MAX_BODY_BYTES = 32 * 1024
KST = timezone(timedelta(hours=9))

app = FastAPI(title="청평의 방명록", docs_url=None, redoc_url=None, openapi_url=None)


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    # DB 파일 자체의 상한은 약 10 MiB. 호스팅 전체 사용량의 상한은 아닙니다.
    page_size = connection.execute("PRAGMA page_size").fetchone()[0]
    connection.execute(f"PRAGMA max_page_count = {10 * 1024 * 1024 // page_size}")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 20),
            message TEXT NOT NULL CHECK(length(message) BETWEEN 1 AND 500),
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection


def render_page(page=1, error="", name="", message="", status_code=200):
    with closing(connect_db()) as connection:
        total = connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, last_page)
        entries = connection.execute(
            "SELECT * FROM entries ORDER BY id DESC LIMIT ? OFFSET ?",
            (PAGE_SIZE, (page - 1) * PAGE_SIZE),
        ).fetchall()

    cards = []
    for entry in entries:
        cards.append(
            '<article class="entry">'
            f'<div class="entry-heading"><strong>{escape(entry["name"])}</strong>'
            f'<time>{escape(entry["created_at"])}</time></div>'
            f'<p>{escape(entry["message"])}</p></article>'
        )
    navigation = []
    if page > 1:
        navigation.append(f'<a href="/?page={page - 1}">이전</a>')
    navigation.append(f'<span>{page} / {last_page}</span>')
    if page < last_page:
        navigation.append(f'<a href="/?page={page + 1}">다음</a>')

    values = {
        "error": f'<p class="error" role="alert">{escape(error)}</p>' if error else "",
        "name": escape(name, quote=True),
        "message": escape(message),
        "count": str(total),
        "entries": "".join(cards) or '<p class="empty">첫 번째 인사를 남겨주세요.</p>',
        "navigation": " ".join(navigation),
    }
    # 사용자 입력에 포함된 치환 기호가 다시 처리되지 않도록 원본을 한 번만 순회합니다.
    template = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    parts = template.split("{{")
    output = [parts[0]]
    for part in parts[1:]:
        key, rest = part.split("}}", 1)
        output.append(values[key] + rest)
    return HTMLResponse("".join(output), status_code=status_code)


def save_entry(name, message):
    with closing(connect_db()) as connection:
        with connection:
            # 개수 확인과 저장을 묶어 동시 등록에도 1,000건 상한을 지킵니다.
            connection.execute("BEGIN IMMEDIATE")
            total = connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            if total >= MAX_ENTRIES:
                return False
            connection.execute(
                "INSERT INTO entries (name, message, created_at) VALUES (?, ?, ?)",
                (name, message, datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")),
            )
    return True


@app.middleware("http")
async def response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'self'; form-action 'self'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/", response_class=HTMLResponse)
def index(page: int = Query(default=1, ge=1, le=10000)):
    return render_page(page=page)


@app.get("/style.css")
def stylesheet():
    return Response((BASE_DIR / "style.css").read_text(encoding="utf-8"), media_type="text/css")


@app.post("/entries", response_class=HTMLResponse)
async def create_entry(request: Request):
    # 일반 브라우저가 다른 사이트에서 전송한 폼을 거부합니다.
    origin = request.headers.get("origin")
    if origin and (
        origin == "null" or urlsplit(origin).netloc != request.url.netloc
        or urlsplit(origin).scheme != request.url.scheme
    ):
        return HTMLResponse("다른 사이트에서의 등록 요청은 허용하지 않습니다.", status_code=403)
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/x-www-form-urlencoded":
        return HTMLResponse("HTML 방명록 양식으로 등록해주세요.", status_code=415)

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY_BYTES:
            return HTMLResponse("요청 내용이 너무 큽니다.", status_code=413)
    try:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True,
                        encoding="utf-8", errors="strict", max_num_fields=2)
        if set(form) != {"name", "message"} or any(len(value) != 1 for value in form.values()):
            raise ValueError("잘못된 양식")
        name = form["name"][0].strip()
        message = form["message"][0].strip()
    except (ValueError, UnicodeError):
        return HTMLResponse("이름과 내용을 올바른 양식으로 보내주세요.", status_code=400)

    if not 1 <= len(name) <= 20 or not 1 <= len(message) <= 500 or "\x00" in name + message:
        return await run_in_threadpool(
            render_page, error="이름은 1~20자, 내용은 1~500자로 입력해주세요. 공백만 입력할 수 없습니다.",
            name=name[:20], message=message[:500], status_code=422,
        )
    try:
        saved = await run_in_threadpool(save_entry, name, message)
    except sqlite3.OperationalError:
        return HTMLResponse("저장 공간이 부족하거나 일시적으로 사용 중입니다. 잠시 후 다시 시도해주세요.", status_code=503)
    if not saved:
        return await run_in_threadpool(
            render_page, error="방명록이 1,000건에 도달했습니다. 운영자에게 문의해주세요.", status_code=409,
        )
    # 등록 후 GET으로 이동하여 새로고침으로 같은 글이 재등록되는 것을 줄입니다.
    return RedirectResponse(url="/", status_code=303)
