# Day1~Day8 청평의 방명록

Python + 기존 FastAPI + HTML/CSS + 내장 SQLite로 만든 학습용 방명록입니다. 이름과 내용을 등록하고 최신순으로 조회합니다. JavaScript, React, Vue, ORM, 외부 DB, 유료 API는 사용하지 않습니다.

## 빠른 실행 — Windows PowerShell

Python 3.12 기준입니다. 저장소 루트 `C:\AI_04기`에서 실행합니다.

```powershell
cd C:\AI_04기\day1-day8
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

현재 작업에서는 이 폴더에 정상적인 `.venv`를 새로 생성하고 개발용 의존성까지 설치했습니다. 이 컴퓨터에서는 마지막 명령부터 실행할 수 있습니다. 다른 컴퓨터로 `.venv`를 복사하지 말고 새로 생성하세요. `python` 명령이 없으면 Python 3.12를 설치하고 PATH를 설정합니다. 기존 루트 `.venv`는 실행 경로가 끊어져 있으며 수정하지 않았습니다.

브라우저에서 <http://127.0.0.1:8000>에 접속합니다. `index.html`을 직접 열면 저장 기능은 동작하지 않습니다. 서버 종료는 Ctrl+C입니다.

### `ERR_CONNECTION_REFUSED`가 나오는 경우

주소를 열기 전에 위 서버 실행 명령을 실행하고, 터미널에 `Uvicorn running on http://127.0.0.1:8000`이 나오는지 확인하세요. 실행 중에는 터미널을 닫지 않습니다.

`did not find executable`이 나오면 가상환경이 가리키는 Python이 없다는 뜻입니다. 정상적인 Python 3.12로 가상환경을 복구해야 합니다. 기존 루트 `.venv`가 활성화된 상태에서 `python -m venv .venv`를 다시 실행하지 마세요. 먼저 `deactivate`로 빠져나오고 정상 설치된 Python 실행 파일을 사용하세요.

`--reload` 실행이 실패하면서 포트만 점유한 경우 기존 방명록 실행 터미널에서 Ctrl+C로 종료하고 위 명령으로 다시 시작합니다. 다른 프로그램을 임의로 종료하지 않습니다. 이번 실행 명령은 자동 재시작 옵션을 생략했습니다.

## 파일 안내

| 파일 | 내용 |
|---|---|
| `main.py` | HTML 응답, 입력 검증, SQLite 저장·목록 |
| `index.html`, `style.css` | 한 화면의 HTML 양식과 반응형 CSS |
| `requirements.txt` | 기존 Day8 실행 라이브러리 버전 |
| `requirements-dev.txt`, `test_app.py` | 기존 Day8 테스트 도구와 검증 코드 |
| `ANALYSIS.md` | Day별 코드 분석과 방명록 적용 근거 |
| `GUIDE.md` | 구현 절차·DB 구조·유지보수 |
| `DEPLOYMENT.md` | 무료 배포 추천·한계·상세 절차 |
| `VERIFICATION.md` | 검증 결과 및 미검증 범위 |

DB는 첫 접속 시 `data/guestbook.db`에 자동 생성됩니다. 사용자 테이블은 `entries` 하나입니다. 사용자 글이나 DB 파일을 Git에 올리지 않도록 `.gitignore`에 제외했습니다.

## 범위

- 이름 1~20자, 내용 1~500자, 공백만 있는 입력 거절
- 최신순, 페이지당 20건, 최대 1,000건 등록 후 새 글 거절
- SQL 매개변수와 HTML 이스케이프로 입력을 데이터로 처리
- 회원가입·로그인·수정·삭제·첨부파일·검색은 이번 범위에 포함하지 않음
- 운영자 기능, 스팸 방지 서비스, 템플릿 엔진 등 새 라이브러리나 알고리즘 추가는 사용자에게 먼저 문의

로컬 DB 용량 제한만으로 호스팅의 트래픽·빌드·로그 사용량을 제한할 수는 없습니다. 무료 플랜의 데이터 보존 조건은 배포 가이드를 먼저 확인하세요. 실제 외부 배포와 계정 생성은 수행하지 않았습니다.
