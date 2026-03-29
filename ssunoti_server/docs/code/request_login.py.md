# request_login.py

## 목적

SSU 통합 로그인(SSO)을 `requests` 라이브러리로 자동화하는 모듈.
브라우저 없이 HTTP 요청만으로 `path.ssu.ac.kr` 인증 세션을 획득한다.

---

## 개요

숭실대 SSO는 `smartid.ssu.ac.kr`에서 인증을 처리한 뒤, 인증 토큰(`sToken`)을 URL 파라미터에 담아 `path.ssu.ac.kr`로 전달하는 구조다.
이 과정이 브라우저에서는 JavaScript `parent.location.href`로 처리되기 때문에, `requests`로는 JS를 실행할 수 없으므로 응답 body를 직접 파싱해 리다이렉트 URL을 추출한다.

---

## 로그인 플로우

```
[1단계] GET smln.asp?apiReturnUrl=...
        → ASPSESSIONID 쿠키 발급 (ASP 서버 세션 식별자)

[2단계] POST smln_pcs.asp (userid, pwd)
        → sToken, sAddr 쿠키 발급
        → 응답 body에 JS 리다이렉트 URL 포함
          parent.location.href = 'https://path.ssu.ac.kr/comm/login/user/loginProc.do?...&sToken=...&sIdno=...'

[3단계] GET loginProc.do?sToken=...&sIdno=...
        → JSESSIONID 발급 (path.ssu.ac.kr 세션 완성)
        → 이후 session으로 path.ssu.ac.kr 인증 요청 가능
```

---

## 주요 구성요소

### 상수

| 상수 | 값 | 설명 |
|------|-----|------|
| `SSO_LOGIN_PAGE` | `https://smartid.ssu.ac.kr/Symtra_sso/smln.asp` | SSO 로그인 폼 페이지 |
| `SSO_LOGIN_PROCESS` | `https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp` | SSO 로그인 처리 엔드포인트 |
| `API_RETURN_URL` | `https://path.ssu.ac.kr/comm/login/user/loginProc.do?...` | 로그인 성공 후 돌아올 URL |

---

### `create_session() -> requests.Session`

브라우저처럼 보이는 기본 헤더가 설정된 세션을 생성한다.

**설정 헤더:**
- `User-Agent`: Chrome 146 (macOS)
- `Accept`: HTML 문서 형식
- `Accept-Language`: 한국어 우선

---

### `login(session) -> bool`

SSO 3단계 로그인을 수행한다.

**파라미터:**
- `session`: `create_session()`으로 생성한 Session 객체

**반환값:**
- `True`: 로그인 성공 (JSESSIONID 발급됨)
- `False`: 로그인 실패 (JS 리다이렉트 URL 파싱 실패 또는 JSESSIONID 미발급)

**자격증명 출처:**
- `.env` 파일의 `student_no` (학번), `ssu_pw` (비밀번호)

---

## 의존성

### 이 파일이 의존하는 것

| 의존성 | 용도 |
|--------|------|
| `requests` | HTTP 세션 관리 |
| `python-dotenv` | `.env`에서 자격증명 로드 |
| `re` (표준 라이브러리) | JS 응답 body에서 리다이렉트 URL 파싱 |
| `.env` 파일 | `student_no`, `ssu_pw` 값 |

### 이 파일에 의존하는 것

- 비교과 프로그램 크롤링 등 `path.ssu.ac.kr` 인증이 필요한 모든 스크립트

---

## 사용 예시

### 기본 로그인

```python
from crawling_browser.request_login import create_session, login

session = create_session()
success = login(session)

if success:
    # 인증된 세션으로 페이지 요청
    res = session.get("https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do")
    print(res.status_code)  # 200
```

### 비교과 프로그램 목록 파싱

```python
from bs4 import BeautifulSoup
from crawling_browser.request_login import create_session, login

session = create_session()
login(session)

res = session.get("https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do")
soup = BeautifulSoup(res.text, "lxml")

items = soup.select(".lica_wrap ul li a.tit")
for item in items:
    print(item.text.strip())
```

---

## 주의사항

- **JS 리다이렉트 파싱**: SSO 응답이 HTTP 리다이렉트가 아닌 JS(`parent.location.href`)로 처리됨. `allow_redirects=False`로 POST해야 body를 읽을 수 있음.
- **sToken URL 파라미터**: `sToken`은 쿠키가 아니라 `loginProc.do`의 쿼리 파라미터로 전달됨. 세션 쿠키(`.ssu.ac.kr` 도메인)와 별개.
- **Referer 필수**: `loginProc.do` 호출 시 Referer가 없으면 `error_referer.jsp`로 이동됨.
- **세션 만료**: `JSESSIONID`는 서버 설정에 따라 만료됨. 만료 시 로그인 페이지로 리다이렉트되므로 `res.url`로 확인 필요.
- **자격증명 보안**: `.env` 파일을 `.gitignore`에 반드시 포함할 것.

---

## 최종 수정일

2026-03-26