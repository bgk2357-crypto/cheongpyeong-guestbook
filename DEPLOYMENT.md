# 청평의 방명록 — 무료 배포 따라 하기

배포는 **내 컴퓨터의 방명록 파일을 인터넷 서버에 올려서, 다른 사람도 주소로 접속하게 만드는 작업**입니다. 배포하면 `127.0.0.1` 대신 공유할 수 있는 HTTPS 주소가 생깁니다.

## 처음 시작한다면 여기부터 읽으세요

먼저 목적을 구분하세요.

| 목적 | 따라갈 방법 |
|---|---|
| 외부에서 화면과 등록 기능을 잠깐 시연하고 싶다 | 아래 **Render 1~8단계** |
| 사람들이 쓴 응원글을 계속 보관하고 싶다 | 아래 **PythonAnywhere 상세 절차**. 무료 FastAPI 지원 여부를 먼저 확인 |

**Render 무료 배포는 재시작하면 응원글이 사라집니다.** 현재 앱이 글을 SQLite 파일에 저장하기 때문입니다. 글 보관이 목적이면 Render 시연 절차를 운영용으로 사용하지 마세요. [공식 데이터 보존 정책](https://render.com/docs/free)

PythonAnywhere는 FastAPI 실행 기능이 실험 단계이고 장기 요금도 확정되지 않았습니다. 현재 앱을 그대로 유지하면서 글도 보존하는 영구 무료 배포를 보장할 수는 없습니다. [공식 지원 안내](https://help.pythonanywhere.com/pages/ASGICommandLine/)

## Render로 시연하기: 1단계 — 준비물 확인

필요한 것은 GitHub 계정, Render 계정, 방명록 파일입니다. 새 라이브러리를 추가할 필요는 없습니다. 이 안내는 파일 준비부터 설명하며 실제 가입이나 배포를 대신 수행한 것은 아닙니다.

## 2단계 — 올릴 파일 5개 준비

내 컴퓨터에서 `C:\AI_04기\day1-day8` 폴더를 엽니다. 아래 **5개 파일만** 사용할 것입니다. 파일 이름과 확장자를 그대로 유지하세요.

```text
main.py
index.html
style.css
requirements.txt
.gitignore
```

`.venv`, `data`, `guestbook.db`, 로그 파일은 올리지 않습니다. `.gitignore`만 올려도 브라우저 수동 업로드에서 DB가 자동 제외되는 것은 아니므로 파일을 직접 구분하세요. 이 절차는 기존 로컬 글을 이전하지 않습니다.

## 3단계 — GitHub 저장소 만들고 파일 올리기

저장소는 인터넷에 코드를 보관하는 폴더라고 생각하면 됩니다.

1. [GitHub](https://github.com)에 로그인합니다.
2. 오른쪽 위 `+` → `New repository`를 선택합니다.
3. Repository name에 `cheongpyeong-guestbook`을 입력합니다.
4. 공개 범위를 선택합니다. `Public`이면 업로드한 코드를 누구나 볼 수 있습니다. `Private`이면 이후 Render 연결에서 해당 저장소 접근을 허용해야 합니다.
5. `Create repository`를 누릅니다.
6. 빈 저장소 화면의 `uploading an existing file` 링크를 선택합니다. 파일이 있는 저장소라면 `Add file → Upload files`로 들어갑니다.
7. 2단계의 5개 파일을 올리고 `Commit changes`를 누릅니다.

완료 확인: 저장소 첫 화면에서 `main.py`, `index.html`, `style.css`, `requirements.txt`, `.gitignore`가 바로 보여야 합니다. 이 쉬운 절차에서는 `day1-day8` 폴더 전체를 올리지 않습니다.

## 4단계 — Render에서 저장소 연결

1. [Render](https://dashboard.render.com)에 로그인합니다.
2. `New` 또는 `New +` → **Web Service**를 선택합니다.
3. GitHub 연결을 선택하고 방금 만든 저장소에 대한 접근을 허용합니다.
4. `cheongpyeong-guestbook` 저장소를 선택합니다.

이 앱은 Python 서버가 실행되어야 하므로 서비스 종류는 `Web Service`입니다. [Render의 FastAPI 배포 안내](https://render.com/docs/deploy-fastapi)

## 5단계 — 설정값 입력

아래 값을 그대로 입력합니다. 3단계처럼 파일 5개를 저장소 맨 위에 올린 경우입니다.

| 화면 항목 | 입력할 값 |
|---|---|
| Name | `cheongpyeong-guestbook` — 이미 사용 중이면 뒤에 숫자 추가 |
| Language / Runtime | `Python 3` |
| Branch | 파일을 올린 브랜치, 보통 `main` |
| Region | 선택 가능한 지역 중 하나 |
| Root Directory | **비워두기** |
| Build Command | `python -m pip install -r requirements.txt` |
| Start Command | `python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Instance Type | **Free** |

Environment Variables에서 다음 항목도 추가합니다.

| Key | Value |
|---|---|
| `PYTHON_VERSION` | `3.12.10` |

`$PORT`는 Render가 정하는 포트입니다. `8000`으로 바꾸지 마세요. Python 버전이 지원되지 않는다는 메시지가 나오면 Render에서 지원하는 3.12 패치 버전을 확인하세요.

추가 DB나 디스크는 만들지 않습니다. 결제 수단을 등록하지 않은 무료 사용에서는 전송량 한도 초과 시 서비스가, 빌드 한도 초과 시 새 빌드가 중지된다고 안내되어 있습니다. 이미 결제 수단이 등록된 계정은 초과 과금과 지출 제한 설정을 확인하세요. [Render 무료 사용량 정책](https://render.com/docs/free)

## 6단계 — 배포 시작

`Create Web Service`를 누르고 로그를 확인합니다. Render가 필요한 패키지를 설치하고 서버를 시작합니다. 상태가 `Live`로 바뀌면 배포된 주소를 엽니다.

주소는 다음과 같은 형태입니다. 아래는 예시이며 실제 주소는 Render 화면에서 복사하세요.

```text
https://cheongpyeong-guestbook.onrender.com
```

완료 확인: 화면에 **청평의 방명록**이 보입니다. 이 주소가 다른 사람에게 공유할 주소입니다.

## 7단계 — 휴대전화로 확인

1. 휴대전화 Wi-Fi를 끄고 모바일 데이터를 켭니다.
2. Render에서 복사한 HTTPS 주소에 접속합니다.
3. 이름과 응원글을 입력해 등록합니다.
4. 새로고침한 뒤 방금 등록한 글이 보이는지 확인합니다.

호스팅 서버에서 실행되므로 내 PC의 Uvicorn이나 공유기 포트포워딩은 필요 없습니다. 로컬 DB와 배포 서버 DB는 별개입니다.

## 8단계 — 이후 수정하는 방법

내 컴퓨터에서 파일 수정 → 변경한 파일을 GitHub에 업로드하고 `Commit changes` → Render 배포 확인 순서입니다. 자동 배포가 켜져 있으면 커밋 후 배포가 진행됩니다. 꺼져 있으면 Render에서 수동 배포를 실행합니다.

**Render Free에서는 이 재배포 과정에서도 기존 응원글이 사라집니다.** 또한 15분간 요청이 없으면 정지할 수 있고, 다음 접속 때 다시 켜지는 동안 기다릴 수 있습니다. [무료 서비스 동작](https://render.com/docs/free)

## 잘 안 될 때 확인할 것

| 증상 | 먼저 확인할 것 |
|---|---|
| `requirements.txt`를 못 찾음 | GitHub 맨 위에 파일이 있는지, Root Directory를 비웠는지 |
| `Could not import module main` | `main.py` 이름과 저장 위치 |
| 화면은 열리는데 CSS가 안 보임 | `style.css` 업로드 여부 |
| 접속할 때 한동안 대기 화면이 나옴 | 무료 서비스가 다시 켜지는 중인지 |
| 수정한 문구가 안 보임 | GitHub 커밋과 Render 새 배포 완료 여부 |
| 응원글이 사라짐 | Render 무료 서버가 재시작·재배포·유휴 정지했는지 |

---

## 상세 참고: 글 보존이 필요한 경우와 기존 저장소 배포

아래는 PythonAnywhere의 조건부 배포 방법과 저장소 전체를 올릴 때의 설정입니다. Render 시연만 진행한다면 위 1~8단계까지 따라 하면 됩니다.

정책 확인일: **2026-10-23**. 계정별 제공 여부와 요금 화면은 실제 배포 직전에 다시 확인하세요. 이 작업은 코드와 절차 작성까지이며 외부 계정 생성·서비스 공개·결제 등록은 수행하지 않았습니다.

## 어떤 사이트를 선택할까?

| 후보 | 이 앱과의 적합성 | 추천 용도 |
|---|---|---|
| PythonAnywhere 무료 계정 | SQLite 사용 가능. 단 FastAPI용 ASGI가 실험 기능이며 장기 가격 미확정 | **계정에서 무료 ASGI 이용이 가능한지 확인한 뒤**, 파일을 보존하는 소규모 학습용 방명록 후보 |
| Render Free Web Service | 기존 FastAPI 그대로 실행 가능. 재시작·재배포·유휴 정지 때 SQLite 파일 변경이 사라짐 | 데이터가 사라져도 되는 단기 시연 |

SQLite 지원은 [PythonAnywhere DB 문서](https://help.pythonanywhere.com/pages/KindsOfDatabases), ASGI의 제한은 [공식 ASGI 안내](https://help.pythonanywhere.com/pages/ASGICommandLine/)에서 확인했습니다. 따라서 PythonAnywhere가 이 요구에 더 맞는다는 것은 파일 DB 조건에 따른 판단이며, 영구 무료 FastAPI 운영을 보장한다는 뜻은 아닙니다.

PythonAnywhere 무료 계정은 디스크 512 MiB, 웹앱 1개·worker 1개, 만료 기간 1개월 등의 제한이 있습니다. 공식 문서의 100 CPU seconds 항목은 별도의 계정 자원 지표이므로 웹 요청 수로 환산하지 않습니다. [무료 계정 기능](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)

**FastAPI 유지 + SQLite 파일 보존 + 안정적인 영구 무료라는 조합은 확인한 자료만으로 보장할 수 없습니다.** 무료 ASGI 이용이 안 되면 그 지점에서 중단하고 사용자와 대안을 정합니다. Flask 전환, 외부 DB, 유료 디스크를 임의로 도입하지 않습니다.

## A. PythonAnywhere — 파일 보존이 필요한 학습용 후보

### 1. 계정과 지원 조건 확인

1. [PythonAnywhere](https://www.pythonanywhere.com/pricing/)에서 무료 계정을 선택합니다. 아래 예시는 미국 서버 기준입니다.
2. 계정에서 실험 ASGI 기능을 무료로 이용할 수 있는지 확인합니다. 불명확하면 공식 지원에 직접 확인합니다. 이미 있는 웹앱을 덮어쓰지 않습니다.
3. 무료 계정 웹앱 만료일을 확인하고, 계속 사용하려면 만료 전에 제공되는 연장 방법을 확인합니다. ASGI 관리 화면이 없으면 공식 안내의 지원 경로를 확인합니다.

### 2. 필요한 소스만 업로드

Files 화면에서 `/home/YOURUSERNAME/guestbook` 폴더를 만들고 다음 4개 파일을 업로드합니다. `YOURUSERNAME`은 본인의 사용자 이름으로 바꿉니다.

```text
main.py
index.html
style.css
requirements.txt
```

`.venv`, 테스트 출력, 기존 DB, 다른 Day 폴더는 업로드하지 않습니다. 서버에서 DB를 새로 생성합니다. 기존 글을 이전하려면 별도로 백업·이전 여부를 결정합니다.

### 3. 기존 라이브러리만 설치

PythonAnywhere의 Bash console에서 실행합니다. 3.12가 제공되지 않는 계정에서는 제공되는 Python 3.10 이상 중 의존성이 설치되는 버전을 먼저 확인합니다.

```bash
cd /home/YOURUSERNAME/guestbook
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

앱에서 `style.css` 경로를 직접 응답하므로 ASGI의 static mapping을 추가할 필요가 없습니다. `uvicorn[standard]` 같은 추가 패키지도 설치하지 않습니다.

### 4. 표준 라이브러리로 ASGI 앱 생성

공식 문서는 `pa` 도구를 권장하지만 새 외부 도구를 추가하지 않기 위해 아래는 [공식 API 형식](https://help.pythonanywhere.com/pages/ASGIAPI/)을 Python 표준 `urllib.request`로 호출하는 방법입니다. **이 단계는 실제 웹앱을 공개합니다.** 무료 지원과 도메인 사용 여부를 확인한 뒤 진행합니다.

Account의 API token 화면에서 토큰을 생성합니다. 토큰은 파일·Git·채팅에 붙여 넣지 않습니다. Bash에서 `.venv/bin/python`으로 Python 콘솔을 열고 다음을 실행합니다. 토큰은 입력 프롬프트에서만 입력하며 화면에 표시되지 않습니다.

```python
import getpass
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

username = input("PythonAnywhere 사용자 이름: ").strip()
token = getpass.getpass("API token: ")
host = "www.pythonanywhere.com"
domain = f"{username}.pythonanywhere.com"
base = f"https://{host}/api/v1/user/{username}/"
command = (
    f"/home/{username}/guestbook/.venv/bin/uvicorn "
    f"--app-dir /home/{username}/guestbook "
    "--uds ${DOMAIN_SOCKET} --workers 1 main:app"
)
payload = {"domain_name": domain, "enabled": True, "webapp": {"command": command}}
request = Request(
    base + "websites/",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urlopen(request, timeout=30) as response:
        print("생성 응답:", response.status)
except HTTPError as error:
    print("생성 실패:", error.code, "계정 지원·무료 조건·도메인 중복을 확인하세요.")
```

EU 계정이면 `host`는 `eu.pythonanywhere.com`, `domain`은 `사용자이름.eu.pythonanywhere.com`으로 바꿉니다. `${DOMAIN_SOCKET}`는 그대로 둡니다. 서비스가 제공하는 소켓 값으로 실행 시 치환됩니다. API는 실험 기능이어서 형식이 달라지면 공식 문서를 다시 확인합니다. 401/403은 토큰·계정 지원 여부, 충돌 오류는 기존 앱 여부를 확인하며, 유료 플랜으로 자동 전환하지 않습니다.

### 5. 접속·갱신·데이터 보존 검증

`https://YOURUSERNAME.pythonanywhere.com`에 접속해 글을 등록합니다. CSS, 한글, 줄바꿈을 확인합니다. 서버 Files 화면에서 `guestbook/data/guestbook.db`가 생성되었는지 확인합니다.

소스 업데이트 후에는 공식 API의 reload를 호출합니다. 같은 Python 콘솔에서 아래를 실행할 수 있습니다. 새 콘솔이라면 앞 단계의 username, token, base, domain을 다시 설정합니다.

```python
reload_request = Request(
    base + f"websites/{domain}/reload",
    data=b"",
    headers={"Authorization": f"Token {token}"},
    method="POST",
)
with urlopen(reload_request, timeout=30) as response:
    print("재시작 응답:", response.status)
```

재시작 후 등록한 글이 남아 있어야 합니다. 서버 DB를 빈 로컬 DB로 덮어쓰지 않습니다. 장기 보존은 계정 유지 정책과 백업에도 달려 있습니다. 사용량 화면에서 가상환경·로그·DB·백업을 합한 디스크 사용량을 확인합니다.

SQLite는 파일 시스템 성능의 영향을 받고 다중 worker 운용 시 문제가 생길 수 있으므로 이번 앱은 worker 1개를 유지합니다. [PythonAnywhere 성능 안내](https://help.pythonanywhere.com/pages/MySiteIsSlow/)

## B. Render — 데이터 유실을 허용하는 무료 시연

Render 무료 서비스는 유휴 15분 후 정지할 수 있습니다. SQLite 파일은 정지·재시작·재배포 시 보존되지 않으며, 무료 서비스에는 영구 디스크를 붙일 수 없습니다. 월 무료 실행 시간은 workspace 전체 750시간입니다. 무료 Postgres로 바꾸는 방식은 이번 내장 DB 조건에 맞지 않습니다. [Render 무료 정책](https://render.com/docs/free)

### 배포 순서

1. GitHub 등에 방명록 소스만 담은 저장소를 준비합니다. GitHub Pages 정적 호스팅을 선택하는 절차가 아닙니다.
2. `main.py`, `index.html`, `style.css`, `requirements.txt`, `.gitignore`를 올립니다. `.venv`, `data`, 토큰, 테스트용 DB는 제외합니다.
3. Render에서 **New → Web Service**로 소스 저장소를 연결합니다.
4. Runtime은 Python, Instance Type은 **Free**, worker는 1개로 유지합니다.
5. 아래 설정을 입력합니다.

| 항목 | 이 저장소 전체를 올린 경우 | 방명록 파일만 별도 저장소에 올린 경우 |
|---|---|---|
| Root Directory | `day1-day8` | 비워둠 |
| Build Command | `python -m pip install -r requirements.txt` | 동일 |
| Start Command | `python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` | 동일 |
| 환경 변수 | `PYTHON_VERSION=3.12.10` | 동일 |

6. Create Web Service를 눌러 빌드 로그를 확인합니다. 제공되는 `https://서비스명.onrender.com`에 접속합니다.
7. 글 등록, 오류 입력, 목록 이동을 확인합니다. 재시작 이후 이전 글이 사라지는 것은 이 무료 배포 방식의 한계입니다. 보존이 필요하면 Render 시연을 정식 방명록으로 사용하지 않습니다.

UI와 연결 흐름은 [Render 배포 안내](https://render.com/docs/your-first-deploy)를 따릅니다. 호스트가 제공하는 Python 버전이 바뀌면 지원하는 3.12 패치 버전을 확인하고 설정합니다.

### 무료 비용 점검

유료 인스턴스·디스크·외부 DB를 추가하지 않습니다. 대시보드의 실행 시간, 전송량, 빌드 사용량을 확인합니다. Render는 일부 사용량 초과에 추가 청구 가능성을 안내하므로 **Free 인스턴스만 선택하면 모든 초과 사용이 자동 차단된다고 가정하지 않습니다.** 결제 수단 없는 상태의 처리 방식과 지출 제한 기능을 계정에서 확인하고, 비용 차단이 불명확하면 공개 운영을 시작하지 않습니다. 앱의 건수 제한은 방문 트래픽 제한이 아닙니다. [Render 무료 정책](https://render.com/docs/free)

## 배포 완료 판단

- HTTPS 주소에서 화면과 CSS가 열리고 한글 등록이 된다.
- 빈 입력·초과 길이·다른 사이트 폼 요청이 예상대로 처리된다.
- 21건 이상에서 목록이 페이지당 20건으로 나뉜다.
- DB 파일 URL에 접근해도 다운로드되지 않는다.
- 파일 보존이 필요한 경우 서버 재시작 후에도 글이 남는다.
- 무료 한도와 만료·초과 사용 처리 방식을 확인했다.

이 중 파일 보존이나 비용 조건을 충족하지 못하면 배포 방식의 한계로 기록하고 다른 기술·요금제로 임의 변경하지 않습니다.
