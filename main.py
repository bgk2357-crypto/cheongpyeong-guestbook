"""청평의 방명록: Supabase에 글을 저장하고 조회합니다."""

import logging
import os
from contextlib import asynccontextmanager
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from httpx import HTTPError
from postgrest.exceptions import APIError
from supabase import Client, create_client

BASE_DIR = Path(__file__).resolve().parent
PAGE_SIZE = 20
MAX_BODY_BYTES = 32 * 1024
logger = logging.getLogger("uvicorn.error")


def check_database(database: Client):
    database.table("entries").select("id").limit(1).execute()


@asynccontextmanager
async def lifespan(application: FastAPI):
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL과 SUPABASE_SECRET_KEY를 설정하세요.")
    if not url.startswith("https://") or not key.startswith("sb_secret_"):
        raise RuntimeError("Supabase Project URL과 서버용 Secret key를 확인하세요.")
    application.state.database = create_client(url, key)
    try:
        await run_in_threadpool(check_database, application.state.database)
    except (APIError, HTTPError):
        raise RuntimeError("Supabase 연결 실패: URL, Secret key, entries 권한을 확인하세요.") from None
    logger.info("Guestbook database: Supabase (entries)")
    yield


app = FastAPI(
    title="청평의 방명록",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def render_page(database, page=1, error="", name="", message="", status_code=200):
    result = database.table("entries").select("id", count="exact").limit(1).execute()
    if result.count is None:
        raise RuntimeError("Supabase에서 글 개수를 반환하지 않았습니다.")
    total = result.count
    last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, last_page))
    start = (page - 1) * PAGE_SIZE
    entries = (
        database.table("entries")
        .select("id,name,message,created_at")
        .order("id", desc=True)
        .range(start, start + PAGE_SIZE - 1)
        .execute()
        .data
    )

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
    template = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    parts = template.split("{{")
    output = [parts[0]]
    for part in parts[1:]:
        key, rest = part.split("}}", 1)
        output.append(values[key] + rest)
    return HTMLResponse("".join(output), status_code=status_code)


def save_entry(database, name, message):
    # DB 함수에서 개수 확인과 저장을 순서대로 처리하여 동시 요청의 한도를 지킵니다.
    result = database.rpc(
        "guestbook_add_entry", {"p_name": name, "p_message": message}
    ).execute()
    if not isinstance(result.data, bool):
        raise RuntimeError("Supabase 저장 함수의 반환값이 잘못되었습니다. SQL을 확인하세요.")
    return result.data


@app.middleware("http")
async def response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'self'; img-src 'self'; form-action 'self'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(APIError)
@app.exception_handler(HTTPError)
async def database_error(request: Request, error: Exception):
    # 키, 요청 URL, 사용자가 작성한 내용은 로그에 기록하지 않습니다.
    code = str(getattr(error, "code", "network_error"))[:40]
    logger.error("Supabase request failed: type=%s code=%s", type(error).__name__, code)
    return HTMLResponse(
        '<!doctype html><html lang="ko"><meta charset="utf-8">'
        '<title>저장소 연결 오류</title><h1>저장소에 연결할 수 없습니다.</h1>'
        '<p>잠시 후 다시 시도해 주세요.</p><a href="/">방명록으로 돌아가기</a></html>',
        status_code=503,
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request, page: int = Query(default=1, ge=1, le=10000)):
    return render_page(request.app.state.database, page=page)


@app.get("/style.css")
def stylesheet():
    return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/ocean-sailing.jpg", include_in_schema=False)
def sailing_background():
    return FileResponse(BASE_DIR / "ocean-sailing.jpg", media_type="image/jpeg")


@app.get("/health")
def health(request: Request):
    check_database(request.app.state.database)
    return {"status": "ok", "database": "supabase"}


@app.post("/entries", response_class=HTMLResponse)
async def create_entry(request: Request):
    if request.headers.get("sec-fetch-site") == "cross-site":
        return HTMLResponse("다른 사이트에서의 등록 요청은 허용하지 않습니다.", status_code=403)
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
        form = parse_qs(
            body.decode("utf-8"), keep_blank_values=True,
            encoding="utf-8", errors="strict", max_num_fields=2,
        )
        if set(form) != {"name", "message"} or any(len(v) != 1 for v in form.values()):
            raise ValueError("잘못된 양식")
        name, message = form["name"][0].strip(), form["message"][0].strip()
    except (ValueError, UnicodeError):
        return HTMLResponse("이름과 내용을 올바른 양식으로 보내주세요.", status_code=400)

    database = request.app.state.database
    if not 1 <= len(name) <= 20 or not 1 <= len(message) <= 500 or "\x00" in name + message:
        return await run_in_threadpool(
            render_page, database,
            error="이름은 1~20자, 내용은 1~500자로 입력해주세요. 공백만 입력할 수 없습니다.",
            name=name[:20], message=message[:500], status_code=422,
        )
    saved = await run_in_threadpool(save_entry, database, name, message)
    if not saved:
        return await run_in_threadpool(
            render_page, database,
            error="방명록이 1,000건에 도달했습니다. 운영자에게 문의해주세요.",
            name=name, message=message, status_code=409,
        )
    return RedirectResponse(url="/", status_code=303)

