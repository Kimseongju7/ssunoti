# BeautifulSoup 사용법

Python HTML/XML 파싱 라이브러리. `pip install beautifulsoup4 lxml`로 설치.

---

## 개요

`BeautifulSoup`은 HTML 문서를 트리 구조로 파싱해 원하는 요소를 쉽게 찾고 추출할 수 있게 해주는 라이브러리다.
`requests`로 받아온 HTML을 분석할 때 주로 사용한다.

---

## 상세 설명

### 파서 종류

```python
from bs4 import BeautifulSoup

html = "<html>...</html>"

soup = BeautifulSoup(html, "lxml")      # 빠르고 관대함 (권장)
soup = BeautifulSoup(html, "html.parser")  # 표준 라이브러리, 별도 설치 불필요
soup = BeautifulSoup(html, "html5lib")  # 가장 정확하지만 느림
```

> 크롤링에서는 `lxml`이 속도와 호환성 면에서 가장 좋다.

---

## 사용법

### 기본 임포트

```python
import requests
from bs4 import BeautifulSoup

res = requests.get("https://example.com")
soup = BeautifulSoup(res.text, "lxml")
```

---

### 요소 찾기

#### `find()` — 첫 번째 요소 하나

```python
# 태그명으로 찾기
tag = soup.find("h1")

# 속성으로 찾기
tag = soup.find("div", class_="title")
tag = soup.find("input", {"name": "userid"})

# 결과가 없으면 None 반환
if tag:
    print(tag.text)
```

#### `find_all()` — 조건에 맞는 모든 요소 (리스트 반환)

```python
items = soup.find_all("li")
items = soup.find_all("a", class_="btn")

for item in items:
    print(item.text)
```

#### `select()` — CSS 선택자로 찾기 (리스트 반환)

```python
# 클래스
items = soup.select(".lica_wrap ul li")

# ID
title = soup.select_one("#main-title")

# 속성
inputs = soup.select("input[type='hidden']")

# 자식 관계
links = soup.select("div.wrap > ul > li a.tit")
```

#### `select_one()` — CSS 선택자로 첫 번째 요소 하나

```python
item = soup.select_one(".lica_wrap ul li a.tit")
```

---

### 텍스트 추출

```python
tag = soup.find("h1")

tag.text          # 모든 하위 텍스트 포함 (공백 포함)
tag.get_text()    # text와 동일
tag.get_text(strip=True)        # 앞뒤 공백 제거
tag.get_text(separator="\n")    # 하위 요소 사이에 구분자 삽입
tag.string        # 직접 텍스트만 (하위 태그 없을 때만 사용)
```

---

### 속성 추출

```python
tag = soup.find("a")

tag["href"]                 # 속성값 (없으면 KeyError)
tag.get("href")             # 속성값 (없으면 None)
tag.get("href", "#")        # 없을 때 기본값 지정
tag.attrs                   # 모든 속성 딕셔너리
```

---

### 탐색

```python
tag = soup.find("ul")

tag.parent              # 부모 요소
tag.children            # 직접 자식 (iterator)
list(tag.children)      # 리스트로 변환
tag.find("li")          # 하위에서 찾기 (중첩 탐색)
tag.next_sibling        # 다음 형제 (공백 텍스트 포함 주의)
tag.find_next_sibling("li")  # 다음 형제 태그
```

---

## 예시

### SSU PATH 비교과 프로그램 목록 파싱

```python
import requests
from bs4 import BeautifulSoup

res = session.get("https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do")
soup = BeautifulSoup(res.text, "lxml")

items = soup.select(".lica_wrap ul li")
for item in items:
    title = item.select_one("a.tit")
    if title:
        print(title.get_text(strip=True))
```

### 로그인 폼에서 hidden input 추출 (CSRF 토큰 등)

```python
res = session.get("https://example.com/login")
soup = BeautifulSoup(res.text, "lxml")

token = soup.find("input", {"name": "_csrf"})
csrf_value = token["value"] if token else None
```

### 테이블 파싱

```python
rows = soup.select("table tbody tr")
for row in rows:
    cols = row.select("td")
    print([col.get_text(strip=True) for col in cols])
```

---

## 주의사항

- **`find()` vs `select_one()`**: `find()`는 태그명·속성 딕셔너리 방식, `select_one()`은 CSS 선택자 방식. CSS에 익숙하면 `select` 계열이 편하다.
- **`class_` 언더스코어**: `class`는 Python 예약어이므로 `find(class_="name")` 형태로 사용.
- **`tag.text` vs `tag.string`**: 하위에 여러 태그가 있으면 `tag.string`은 `None`을 반환함. 항상 `get_text(strip=True)` 사용을 권장.
- **결과 없음 처리**: `find()`와 `select_one()`은 결과가 없으면 `None`을 반환. 속성 접근 전에 반드시 `None` 체크 필요.
- **동적 페이지**: JS로 렌더링된 콘텐츠는 `requests`로 받은 HTML에 없음. 이 경우 `Browser`(Selenium) 사용 필요.

---

## 관련 자료

- [requests 사용법](requests-guide.md)
- [SSU SSO 로그인 구현](ssu-sso-login-with-requests.md)

---

*최종 수정일: 2026-03-27*