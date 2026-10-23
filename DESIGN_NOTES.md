# 바다와 요트 디자인

- 배경: 푸른 바다와 흰 돛을 펼친 세일링 요트 사진.
- 데스크톱: 왼쪽 350px 글쓰기 영역, 오른쪽 가변 너비의 글 목록.
- 모바일: 820px 이하에서 글쓰기와 목록을 위아래로 배치.
- 반투명 흰 패널과 파란색 버튼으로 글의 가독성을 유지.
- 기존 제목·수료 응원 소개·하단 문구 유지.
- HTML/CSS와 기존 FastAPI만 사용. 새 런타임 라이브러리 없음.

## 이미지

내장 ImageGen 도구로 생성했습니다. 원본 생성 이미지는 작업 도구의 생성 이미지 폴더에 보관하고, 배포용은 프로젝트의 `ocean-sailing.jpg`에 JPEG 품질 85로 압축 저장했습니다. 배포 파일 크기는 253,890바이트입니다. 외부 이미지 서비스나 CDN을 호출하지 않습니다.

FastAPI의 `/ocean-sailing.jpg` 경로로 이미지를 제공하고 CSP에서 같은 서버의 이미지만 허용합니다. 공개 서비스에 적용하려면 새 이미지와 수정한 `main.py`, `index.html`, `style.css`를 함께 올려야 합니다.

생성에 사용한 최종 프롬프트:

> Create a beautiful photorealistic wide landscape background photograph for a Korean encouragement guestbook website. 16:9 composition. Brilliant deep blue and turquoise sea, calm small sunlit waves, elegant white sailing yacht with full white sails positioned on far right third of composition, distant hazy coastline on horizon, pale clear blue sky, warm late afternoon sun, serene uplifting atmosphere, premium coastal travel editorial photography, natural realistic detail. Left two thirds mostly calm open water and sky with generous uncluttered negative space where a website will overlay its own text and white panels. Yacht visible in upper right with sea below. No text, no lettering, no logos, no watermark, no UI. Output one landscape bitmap image.

## 검증

기존 자동 테스트 15개 통과. 배경 이미지 HTTP 200, JPEG 응답, 이미지 허용 CSP를 확인했습니다. 연결된 브라우저가 없어 실제 브라우저 화면의 시각 검증은 수행하지 못했습니다.

이번 작업은 디자인 변경입니다. 외부 DB 도입은 아직 승인되지 않았으므로 기존 SQLite 저장 방식은 유지했습니다. Render Free에서 서버 재시작 시 글이 사라지는 저장 조건은 이 디자인 변경으로 해결되지 않습니다.
