import json
import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

from utils import build_url

load_dotenv()


class SsupathCrawler:

    SSO_LOGIN_PAGE = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp"
    SSO_LOGIN_PROCESS = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
    API_RETURN_URL = "https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart"
    SSUPATH_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do"
    DETAIL_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmInfo.do"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.getenv("user_agent"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9",
        })

    def login(self):
        """
        SSU 통합 로그인(SSO)을 수행합니다.

        로그인 플로우:
        1. GET smln.asp → ASPSESSIONID 쿠키 발급
        2. POST smln_pcs.asp → sToken 쿠키 발급 + JS 리다이렉트 URL 획득
        3. GET loginProc.do (sToken 포함) → JSESSIONID 발급 (path.ssu.ac.kr 세션 완성)

        Returns:
            bool: 로그인 성공 여부 (JSESSIONID 발급 여부로 판단)
        """
        login_page_url = f"{self.SSO_LOGIN_PAGE}?apiReturnUrl={self.API_RETURN_URL}"

        # 1단계: 로그인 페이지 GET → ASPSESSIONID 쿠키 획득
        self.session.get(login_page_url)

        # 2단계: SSO 로그인 POST → sToken 발급 + JS 리다이렉트 URL 획득
        res = self.session.post(
            self.SSO_LOGIN_PROCESS,
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
        self.session.get(redirect_url, headers={"Referer": "https://smartid.ssu.ac.kr/"})
        return True

    def get_current_page_notices(self):
        """
        SSUPath 공고 목록 페이지를 파싱하여 공고 태그 목록을 반환합니다.

        Returns:
            list[Tag]: 공고 li 태그 목록. 파싱 실패 시 빈 리스트.
        """
        res = self.session.get(self.SSUPATH_URL)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'lxml')
        notices = soup.select("div[class='lica_wrap'] > ul > li")

        return notices

    def get_notice_url(self, notice):
        """
        공고 태그에서 상세 페이지 URL을 생성합니다.

        Args:
            notice (Tag): 공고 li 태그

        Returns:
            str: 상세 페이지 URL

        Raises:
            ValueError: data-params 속성이 없거나 파싱 실패 시
        """
        a_tag = notice.find('a')
        if not a_tag or not a_tag.get('data-params'):
            raise ValueError("공고 태그에 data-params 속성이 없습니다.")

        params = json.loads(a_tag['data-params'])
        return build_url(self.DETAIL_URL, params)

    def get_detail(self, url):
        pass
