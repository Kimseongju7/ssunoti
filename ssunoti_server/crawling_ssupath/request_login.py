import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

SSO_LOGIN_PAGE = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp"
SSO_LOGIN_PROCESS = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
API_RETURN_URL = "https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart"


def create_session() -> requests.Session:
    """기본 헤더가 설정된 requests 세션을 생성합니다.

    Returns:
        기본 헤더가 설정된 Session 객체

    Example:
        >>> session = create_session()
        >>> res = session.get("https://path.ssu.ac.kr/")
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })
    return session


def login(session: requests.Session) -> requests.Session:
    """SSU 통합 로그인(SSO)을 수행합니다.

    로그인 플로우:
    1. GET smln.asp → ASPSESSIONID 쿠키 발급
    2. POST smln_pcs.asp → sToken 쿠키 발급 + JS 리다이렉트 URL 획득
    3. GET loginProc.do (sToken 포함) → JSESSIONID 발급 (path.ssu.ac.kr 세션 완성)

    Args:
        session: create_session()으로 생성한 Session 객체

    Returns:
        로그인 성공 여부 (JSESSIONID 발급 여부로 판단)

    Example:
        >>> session = create_session()
        >>> success = login(session)
        >>> print(success)  # True
    """
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
        allow_redirects=False,
    )

    # 응답 body에서 JS 리다이렉트 URL 파싱
    match = re.search(r"parent\.location\.href = '(.+?)'", res.text)
    if not match:
        return False

    redirect_url = match.group(1)

    # 3단계: loginProc.do 호출 → path.ssu.ac.kr JSESSIONID 발급
    session.get(redirect_url, headers={"Referer": "https://smartid.ssu.ac.kr/"})

    return session
