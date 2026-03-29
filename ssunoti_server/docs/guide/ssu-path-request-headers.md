# SSU Path 요청 헤더 분석

`https://path.ssu.ac.kr` 크롤링 시 필요한 HTTP 요청 헤더 분석 문서.

분석 대상 엔드포인트: `POST /ptfol/app/push/unreadCnt.do`

---

## 핵심 헤더 (크롤링 시 반드시 필요)

### `cookie`
서버 인증에 사용되는 세션 정보. 로그인 후 자동 발급되며, 가장 중요한 값들:

| 쿠키 이름 | 설명 |
|-----------|------|
| `JSESSIONID` | Java 서버의 세션 식별자. 로그인 상태 유지에 핵심 |
| `sToken` | SSU Path 자체 인증 토큰 |
| `sAddr` | 서버 내부 IP 주소 (URL 인코딩됨) |
| `_ga*` | Google Analytics 추적 쿠키 (인증과 무관) |
| `popup30` | 팝업 표시 여부 (인증과 무관) |

> `requests.Session()`을 사용하면 로그인 후 쿠키가 자동으로 유지됨

### `ajax: true`
서버가 AJAX 요청임을 식별하는 커스텀 헤더. 없으면 HTML 전체 페이지를 응답하거나 오류가 발생할 수 있음.

```python
headers = {"ajax": "true"}
```

### `x-requested-with: XMLHttpRequest`
jQuery 등 JavaScript 라이브러리가 AJAX 요청 시 자동으로 추가하는 헤더. 서버가 AJAX 요청을 구분하는 데 사용.

```python
headers = {"X-Requested-With": "XMLHttpRequest"}
```

---

## 봇 탐지 우회용 헤더

서버가 정상 브라우저 요청인지 확인하기 위해 검사할 수 있는 헤더들.

### `user-agent`
브라우저 식별 문자열. 없거나 Python 기본값이면 차단될 수 있음.

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
}
```

### `sec-ch-ua` / `sec-ch-ua-mobile` / `sec-ch-ua-platform`
Chrome이 자동으로 추가하는 브라우저 힌트 헤더.

```python
headers = {
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
```

### `sec-fetch-*`
요청 출처와 방식을 나타내는 헤더.

| 헤더 | 값 | 의미 |
|------|-----|------|
| `sec-fetch-dest` | `empty` | 특정 리소스 타입 없음 (AJAX) |
| `sec-fetch-mode` | `cors` | CORS 요청 |
| `sec-fetch-site` | `same-origin` | 같은 도메인에서의 요청 |

---

## 캐시 관련 헤더

```
cache-control: no-cache
pragma: no-cache
```

서버에 캐시된 응답 대신 최신 데이터를 요청. 크롤링 시 동일하게 설정 권장.

---

## 참고: 응답 헤더 주요 내용

### `content-security-policy`
서버가 허용하는 외부 리소스 목록. 크롤링에 직접 영향 없음.

허용된 외부 도메인 중 주목할 것:
- `wss://two.reina.solutions` → WebSocket 연결 (실시간 알림용으로 추정)
- `https://service.syworks.net` → 외부 서비스 연동

### `cross-origin-opener-policy`
Google 로그인 팝업 허용을 위한 헤더. 크롤링과 무관.

---

## requests로 크롤링 시 최소 헤더 구성

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# 로그인
session.post("로그인_엔드포인트", data={
    "userid": "학번",
    "pwd": "비밀번호",
})

# 요청 헤더
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "ajax": "true",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://path.ssu.ac.kr/",
}

res = session.get(
    "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do",
    headers=headers
)
soup = BeautifulSoup(res.text, "lxml")
```

> 차단될 경우 `sec-ch-ua`, `sec-fetch-*` 헤더를 추가로 포함시킬 것