# requests로 숭실대 SSO 로그인 자동화하기

브라우저 없이 Python `requests`만으로 숭실대 통합 로그인(SSO)을 처리하고, 인증이 필요한 페이지를 크롤링하는 방법을 소개합니다.

---

## 배경

숭실대 SSU PATH 시스템(`path.ssu.ac.kr`)은 `smartid.ssu.ac.kr`의 SSO를 통해 로그인합니다.
처음에는 단순히 로그인 POST 요청 하나면 될 거라고 생각했지만, 실제로는 **3단계 플로우**가 필요했습니다.

---

## 문제 분석

브라우저 개발자 도구 Network 탭에서 로그인 과정을 캡처하면 다음 요청이 보입니다.

```
POST https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp
Content-Type: application/x-www-form-urlencoded

userid=학번&pwd=비밀번호
```

응답 상태코드는 `200 OK`이고, 응답 헤더에 리다이렉트(`Location`)가 없습니다.
그런데 브라우저는 어떻게 `path.ssu.ac.kr`로 이동할까요?

응답 body를 보면 정답이 있습니다.

```html
SSO API 연결<br>SSO 토큰 검증성공<br>
<script language=javascript>
    parent.location.href = 'https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart?sToken=Vy3z...&sIdno=20231456';
</script>
```

HTTP 리다이렉트가 아닌 **JavaScript로 리다이렉트**하고 있었습니다. `requests`는 JS를 실행할 수 없으므로, body에서 URL을 직접 파싱해야 합니다.

---

## 로그인 플로우

```
1. GET  smln.asp?apiReturnUrl=...       → ASPSESSIONID 쿠키 발급
2. POST smln_pcs.asp (userid + pwd)     → sToken 쿠키 + JS 리다이렉트 URL 획득
3. GET  loginProc.do?sToken=...         → JSESSIONID 발급 (path.ssu.ac.kr 세션 완성)
```

핵심은 2단계에서 `allow_redirects=False`로 POST해 body를 읽고, 정규식으로 URL을 추출한 뒤 3단계에서 직접 호출하는 것입니다.

---

## 구현

### 사전 준비

`.env` 파일에 자격증명을 저장합니다.

```
student_no=20231234
ssu_pw=your_password
```

패키지 설치:

```bash
pip install requests python-dotenv beautifulsoup4 lxml
```

### 코드

```python
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

SSO_LOGIN_PAGE = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp"
SSO_LOGIN_PROCESS = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
API_RETURN_URL = "https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart"


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })
    return session


def login(session: requests.Session) -> bool:
    login_page_url = f"{SSO_LOGIN_PAGE}?apiReturnUrl={API_RETURN_URL}"

    # 1단계: 로그인 페이지 GET → ASPSESSIONID 쿠키 획득
    session.get(login_page_url)

    # 2단계: SSO 로그인 POST → sToken 발급 + JS 리다이렉트 URL 획득
    res = session.post(
        SSO_LOGIN_PROCESS,
        data={
            "userid": os.getenv("student_no"),
            "pwd": os.getenv("ssu_pw"),
        },
        headers={
            "Referer": login_page_url,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://smartid.ssu.ac.kr",
        },
        allow_redirects=False,  # body를 읽기 위해 리다이렉트 비활성화
    )

    # 응답 body에서 JS 리다이렉트 URL 파싱
    match = re.search(r"parent\.location\.href = '(.+?)'", res.text)
    if not match:
        return False  # 로그인 실패 (아이디/비밀번호 오류 등)

    redirect_url = match.group(1)

    # 3단계: loginProc.do 호출 → path.ssu.ac.kr JSESSIONID 발급
    # Referer가 없으면 error_referer.jsp로 이동됨
    session.get(redirect_url, headers={"Referer": "https://smartid.ssu.ac.kr/"})

    return "JSESSIONID" in session.cookies.get_dict()
```

---

## 사용 예시

로그인 후 비교과 프로그램 목록을 가져오는 예시입니다.

```python
from bs4 import BeautifulSoup

session = create_session()
success = login(session)
print("로그인 성공:", success)  # True

res = session.get("https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do")
soup = BeautifulSoup(res.text, "lxml")

items = soup.select(".lica_wrap ul li a.tit")
for item in items:
    print(item.text.strip())
```

실행 결과:

```
2026-1학기 숭실평화통일연구원 대학생 인턴십
...  (총 58개)
```

---

## 트러블슈팅

### 로그인 후 다시 로그인 페이지로 리다이렉트됨

`session.post()`에서 `allow_redirects=True`(기본값)로 설정하면 JS body를 읽지 못하고 로그인이 완성되지 않습니다. 반드시 `allow_redirects=False`로 설정해야 합니다.

### `error_referer.jsp`로 이동됨

`loginProc.do` 호출 시 `Referer` 헤더가 없으면 서버가 요청을 거부합니다. `Referer: https://smartid.ssu.ac.kr/`를 명시해야 합니다.

### sToken이 발급됐는데 path.ssu.ac.kr 접근 불가

`sToken`은 `.ssu.ac.kr` 도메인 쿠키로 발급되지만, `path.ssu.ac.kr`은 별도의 `JSESSIONID`로 세션을 관리합니다. 3단계 `loginProc.do` 호출을 빠뜨리지 않았는지 확인하세요.

---

## 마치며

SSO 시스템은 HTTP 리다이렉트 대신 JavaScript로 토큰을 전달하는 경우가 많습니다. `requests`로 크롤링할 때는 응답 body를 직접 확인해 JS 리다이렉트 여부를 파악하는 것이 중요합니다.

---

*최종 수정일: 2026-03-26*