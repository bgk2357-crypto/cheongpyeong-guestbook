# Day1~Day8 코드 분석과 적용

분석일: 2026-10-23. 실제 폴더명은 소문자 `day1`~`day8`이며, 결과물은 기존 요청 파일이 있는 `day1-day8`에 저장했습니다. 원본 예제는 수정하지 않았습니다. 아래 내용은 파일을 읽어 정리한 것으로 모든 교육 예제를 실행 검증했다는 의미는 아닙니다.

## 폴더별 근거

| 폴더 | 확인한 파일 | 문법·알고리즘 | 방명록에서의 활용 |
|---|---|---|---|
| Day1 | `day1/day1_app/input_utils.py`, `guessing_game.py`, `main.py`, `index.html` | 함수·모듈, 정수 변환, while, if/elif, 범위 검사, 예외 처리, 난수와 정답 비교 | 작은 함수로 역할 분리, 입력 길이와 빈 값 검사, HTML 화면 구성. 난수 게임은 사용하지 않음 |
| Day2 | `day2/오후/day2-1.py`, `오전/day2-7.py`, `mask_bad_words(10.15).py` | for와 조건별 집계, FizzBuzz 우선순위, dict, assert, 정규식 마스킹, 긴 단어 우선 정렬 | 목록 순회·조건 분기·경계값 테스트 활용. 금지어 정책이 정해지지 않아 마스킹·정렬 알고리즘은 추가하지 않음 |
| Day3 | `day3/오전/day3-3.py`, `day3-5.py`, `오후/day3-4.py` | 클래스·상속·오버라이딩, 리스트·딕셔너리, split, strip, try/except, 누락값 처리 | 텍스트 정리와 잘못된 요청 처리 활용. 간단한 앱이므로 별도 클래스 계층은 만들지 않음 |
| Day4 | `day4/오후/day4-1`, `login.txt` | 확장자 없는 파일의 단편 문자열과 텍스트 파일만 존재 | 학습 코드가 충분하지 않아 문법·알고리즘 수준을 추정하지 않음. 로그인 기능의 근거로 사용하지 않음 |
| Day5 | 폴더 없음 | 분석 불가 | 임의로 학습 내용을 보충하지 않음 |
| Day6 | `day6/ch04_validator/demo.py`, `ch07_fastapi/app.py`, `ch08_project/models.py` | Pydantic 모델·Field·validator, HTTP 경로, GET/POST와 CRUD, 예외 응답 | FastAPI 재사용. HTML 폼은 조건문으로 검사하며 JSON API용 모델 계층을 추가하지 않음 |
| Day7 | `day7/01/fastapi_win_vscode/labs/lesson04.py`, `lesson08/`, `day7/03/main.py`, `shop_async_lab/main.py` | 쿼리 필터·페이지 슬라이싱, 라우터 분리, asyncio·비동기 HTTP, 정적 파일 응답 | 20건 단위 페이지 조회, CSS 응답에 적용. 외부 API·병렬 수집·프런트엔드 JS는 사용하지 않음 |
| Day8 | `day8/lesson_02_parameters/main.py`, `lesson_03_body_validation/main.py`, `lesson_04_ai_test_cases/test_api.py`, `lesson_07_state_scenarios/main.py` | 경로·쿼리 검증, 입력 경계값, pytest 매개변수화, 상태 변화 테스트, 오류·응답 계약 | 입력 오류 상태코드, 등록 전후 DB·응답·페이지 상태 검증 |

## 채택 기술과 제외 근거

기존 `day8/lesson_04_ai_test_cases/requirements.txt`의 FastAPI 0.115.12, Pydantic 2.11.5, Uvicorn 0.34.2를 재사용했습니다. 테스트도 같은 파일의 HTTPX 0.28.1과 pytest 8.3.5를 사용합니다. Pydantic은 FastAPI의 기존 의존성이며 이번 앱에서 별도 모델을 만들지는 않았습니다. FastAPI가 설치하는 Starlette/AnyIO 등은 기존 프레임워크 의존성입니다.

요청에서 명시한 내장 DB는 Python `sqlite3`로 구현했습니다. SQLite의 기본 INSERT·SELECT·COUNT·ORDER BY·LIMIT/OFFSET만 사용합니다. 필터링·추천·비밀번호 암호화 등 별도 알고리즘은 추가하지 않았습니다. 목록 렌더링은 반복문과 문자열 결합입니다.

HTML 폼은 기본 `application/x-www-form-urlencoded` 형식만 받습니다. 표준 `urllib.parse.parse_qs`로 해석해 `python-multipart`를 설치하지 않습니다. 표준 `html.escape`, `pathlib`, `datetime`, `contextlib`는 별도 설치가 필요 없습니다. SQLite 연결은 작업마다 열고 닫으며, 비동기 등록 요청에서 DB 처리는 FastAPI의 기존 스레드풀 도구로 실행합니다.

Jinja2, Flask, SQLAlchemy, React, Vue, npm, Docker, Redis, 외부 저장소, 유료 API를 추가하지 않았습니다. 입력 이스케이프·요청 크기 제한·트랜잭션은 요청한 저장 기능을 안전하게 수행하기 위한 기본 처리입니다.

## 복잡도와 한계

- 목록은 DB에서 20건만 읽고 반복 렌더링합니다. 렌더링 비용은 페이지 크기와 글 길이에 비례합니다.
- id 기본키 역순을 사용해 별도 정렬 알고리즘을 구현하지 않습니다. OFFSET은 뒤 페이지에서 더 많은 행을 건너뛰므로 전체 글을 1,000건으로 제한했습니다.
- SQLite는 단일 파일로 저장하므로 여러 서버 인스턴스 확장에는 적합하지 않습니다. 한 프로세스·한 worker를 기준으로 합니다.
- 새 라이브러리·새 알고리즘·추가 테이블·외부 DB가 필요해지면 먼저 사용자의 동의를 구하는 규칙을 유지합니다.
