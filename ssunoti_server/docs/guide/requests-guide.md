# requests 라이브러리 사용 가이드

Python의 HTTP 요청 라이브러리. `pip install requests`로 설치.

---

## 기본 요청

```python
import requests

# GET
res = requests.get("https://example.com")

# POST
res = requests.post("https://example.com/login", data={"id": "test"})

print(res.status_code)  # 200
print(res.text)         # 응답 HTML
print(res.json())       # 응답 JSON (Content-Type이 JSON일 때)
```

---

## Session

### Session을 써야 하는 이유

`requests.get()`은 매번 독립적인 요청을 보냄. 쿠키가 유지되지 않아 로그인 상태를 유지할 수 없음.

`requests.Session()`은 내부적으로 쿠키 저장소를 가지고 있어, 서버가 발급한 쿠키를 자동으로 저장하고 이후 요청에 자동으로 포함시킴.

```
requests.get()    → 쿠키 없음 → 매번 로그인 필요
requests.Session() → 쿠키 자동 유지 → 로그인 한 번으로 이후 요청 모두 인증됨
```

### Session 기본 사용법

```python
import requests

session = requests.Session()

# 세션에 기본 헤더 설정 (모든 요청에 자동 포함)
session.headers.update({
    "User-Agent": "Mozilla/5.0 ...",
    "X-Requested-With": "XMLHttpRequest",
})

# 요청 (설정한 헤더 + 쿠키 자동 포함)
res = session.get("https://example.com/mypage")
```

---

## 로그인 처리

### 1단계: 로그인 엔드포인트 파악

브라우저 개발자 도구 → Network 탭 → 로그인 버튼 클릭 후 POST 요청 확인.

확인할 항목:
- 요청 URL
- Form Data (파라미터 이름과 값)
- CSRF 토큰 여부

### 2단계: CSRF 토큰 처리

많은 서버는 로그인 폼에 CSRF 토큰을 숨겨두고, 로그인 POST 시 함께 전송해야 함.

```python
from bs4 import BeautifulSoup

session = requests.Session()

# 로그인 페이지 GET → CSRF 토큰 파싱
res = session.get("https://example.com/login")
soup = BeautifulSoup(res.text, "lxml")

# 토큰이 hidden input에 있는 경우
csrf_token = soup.find("input", {"name": "_csrf"})["value"]
```

> CSRF 토큰이 없는 서버도 있음. Network 탭에서 Form Data를 확인해 판단.

### 3단계: 로그인 POST

```python
login_data = {
    "userid": "학번",
    "pwd": "비밀번호",
    "_csrf": csrf_token,  # 없으면 생략
}

res = session.post("https://example.com/login.do", data=login_data)

# 로그인 성공 여부 확인
print(res.status_code)   # 200이면 요청 성공 (로그인 성공과는 다름)
print(res.url)           # 리다이렉트된 URL로 성공 여부 판단 가능
```

### 4단계: 로그인 성공 확인

```python
# 방법 1: 리다이렉트 URL 확인
if "main" in res.url:
    print("로그인 성공")

# 방법 2: 응답 HTML에 특정 텍스트 확인
if "로그아웃" in res.text:
    print("로그인 성공")

# 방법 3: 세션 쿠키 확인
print(session.cookies.get_dict())
# {'JSESSIONID': '...', 'sToken': '...'} 등이 있으면 성공
```

### 5단계: 인증된 페이지 요청

로그인 후 session으로 요청하면 쿠키가 자동 포함됨.

```python
res = session.get("https://example.com/mypage")
soup = BeautifulSoup(res.text, "lxml")
print(soup.select_one(".username").text)
```

---

## 쿠키 직접 관리

### 쿠키 확인

```python
# 딕셔너리로 변환
print(session.cookies.get_dict())

# 특정 쿠키 값
print(session.cookies.get("JSESSIONID"))
```

### 쿠키 수동 설정

브라우저에서 로그인 후 쿠키를 복사해 직접 넣을 때 사용.

```python
session.cookies.update({
    "JSESSIONID": "5144B172809053F0BF9754A1EB553414",
    "sToken": "Vy3zFySF...",
})
```

### 쿠키 저장 및 불러오기

세션을 파일로 저장해두면 매번 로그인하지 않아도 됨 (만료 전까지).

```python
import pickle

# 저장
with open("session.pkl", "wb") as f:
    pickle.dump(session.cookies, f)

# 불러오기
with open("session.pkl", "rb") as f:
    session.cookies.update(pickle.load(f))
```

---

## 세션 만료 처리

서버 세션은 일정 시간 후 만료됨. 만료된 세션으로 요청하면 로그인 페이지로 리다이렉트됨.

```python
def is_logged_in(session: requests.Session) -> bool:
    """세션 유효 여부 확인"""
    res = session.get("https://example.com/mypage")
    return "로그아웃" in res.text  # 로그인 상태 판별 텍스트

def login(session: requests.Session) -> None:
    """로그인 수행"""
    session.post("https://example.com/login.do", data={
        "userid": "학번",
        "pwd": "비밀번호",
    })

def get_page(session: requests.Session, url: str) -> str:
    """세션 만료 시 재로그인 후 요청"""
    if not is_logged_in(session):
        login(session)
    return session.get(url).text
```

---

## 헤더 설정

### 전역 헤더 (모든 요청에 적용)

```python
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "ajax": "true",
})
```

### 개별 요청 헤더 (해당 요청에만 적용)

```python
res = session.get(url, headers={"Referer": "https://example.com/prev-page"})
```

---

## POST 요청 데이터 형식

### Form 데이터 (일반 HTML 폼)

```python
# Content-Type: application/x-www-form-urlencoded
session.post(url, data={"key": "value"})
```

### JSON 데이터 (REST API)

```python
# Content-Type: application/json
session.post(url, json={"key": "value"})
```

> 어떤 형식인지는 Network 탭의 요청 헤더 `Content-Type`으로 확인.

---

## SSU Path 적용 예시

```python
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "ajax": "true",
    "X-Requested-With": "XMLHttpRequest",
})

# 로그인
session.post("https://path.ssu.ac.kr/로그인엔드포인트", data={
    "userid": os.getenv("student_no"),
    "pwd": os.getenv("ssu_pw"),
})

# 비교과 프로그램 목록 페이지 요청
res = session.get(
    "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do",
    headers={"Referer": "https://path.ssu.ac.kr/"},
)

soup = BeautifulSoup(res.text, "lxml")
items = soup.select(".lica_wrap ul li a.tit")
for item in items:
    print(item.text.strip())
```

---

## 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 로그인 페이지로 리다이렉트 | 세션 만료 또는 로그인 실패 | 쿠키 확인, 재로그인 |
| 빈 HTML 응답 | AJAX 요청인데 헤더 누락 | `ajax: true`, `X-Requested-With` 추가 |
| 403 Forbidden | CSRF 토큰 누락 또는 봇 탐지 | 토큰 파싱 후 포함, User-Agent 설정 |
| SSL 오류 | 인증서 문제 | `session.get(url, verify=False)` (임시) |