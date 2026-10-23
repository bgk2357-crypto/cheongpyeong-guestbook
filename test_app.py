"""실제 서비스 DB 대신 임시 SQLite 파일에서 동작을 검증합니다."""

import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "guestbook.db")
    with TestClient(main.app) as test_client:
        yield test_client


def test_empty_page_and_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "첫 번째 인사" in response.text
    assert "<script" not in response.text
    assert client.get("/style.css").headers["content-type"].startswith("text/css")
    assert client.get("/data/guestbook.db").status_code == 404


def test_create_redirect_and_persistence(client):
    response = client.post("/entries", data={"name": "  방문자 ", "message": "안녕하세요\n반갑습니다"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    # 연결을 닫았다가 다시 열어도 저장된 데이터를 읽을 수 있어야 합니다.
    with closing(sqlite3.connect(main.DB_PATH)) as connection:
        assert connection.execute("SELECT name, message FROM entries").fetchone() == ("방문자", "안녕하세요\n반갑습니다")
        assert connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [("entries",)]
    assert "안녕하세요\n반갑습니다" in client.get("/").text
    client.get("/")
    assert "1개" in client.get("/").text


@pytest.mark.parametrize("name,message", [("", "내용"), ("   ", "내용"), ("이름", "\n "), ("가" * 21, "내용"), ("이름", "가" * 501), ("이름", "\x00")])
def test_invalid_input(client, name, message):
    assert client.post("/entries", data={"name": name, "message": message}).status_code == 422
    assert "0개" in client.get("/").text


def test_boundaries_and_html_sql_text(client):
    assert client.post("/entries", data={"name": "가" * 20, "message": "나" * 500}).status_code == 200
    payload = "<script>alert('x')</script>{{entries}}"
    assert client.post("/entries", data={"name": "';DROP TABLE entries", "message": payload}).status_code == 200
    page = client.get("/").text
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
    assert "{{entries}}" in page
    assert "2개" in page


def test_pagination_and_capacity(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_ENTRIES", 21)
    for number in range(21):
        assert client.post("/entries", data={"name": f"손님{number}", "message": "인사"}).status_code == 200
    first = client.get("/").text
    second = client.get("/?page=2").text
    assert first.count('<article class="entry">') == 20
    assert second.count('<article class="entry">') == 1
    assert first.index("손님20") < first.index("손님19")
    assert "손님0</strong>" in second
    assert client.post("/entries", data={"name": "초과", "message": "인사"}).status_code == 409
    assert "2 / 2" in client.get("/?page=9999").text


@pytest.mark.parametrize("page", ["0", "-1", "abc", "10001"])
def test_invalid_page(client, page):
    assert client.get(f"/?page={page}").status_code == 422


def test_bad_requests(client):
    assert client.post("/entries", json={"name": "이름", "message": "내용"}).status_code == 415
    headers = {"content-type": "application/x-www-form-urlencoded"}
    assert client.post("/entries", content="name=a&name=b&message=c", headers=headers).status_code == 400
    assert client.post("/entries", content="name=a", headers=headers).status_code == 400
    assert client.post("/entries", content=b"\xff", headers=headers).status_code == 400
    assert client.post("/entries", content=b"a" * (main.MAX_BODY_BYTES + 1), headers=headers).status_code == 413
    assert client.post("/entries", data={"name": "이름", "message": "내용"}, headers={"origin": "https://elsewhere.example"}).status_code == 403
    assert client.post("/entries", data={"name": "이름", "message": "내용"}, headers={"origin": "http://testserver"}).status_code == 200
