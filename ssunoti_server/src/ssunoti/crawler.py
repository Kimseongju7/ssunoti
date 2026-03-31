import json
import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

from ssunoti.utils import build_url

load_dotenv()


class SsupathCrawler:

    SSO_LOGIN_PAGE = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp"
    SSO_LOGIN_PROCESS = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
    API_RETURN_URL = "https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart"
    SSUPATH_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do"
    DETAIL_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmInfo.do"
    BASE_URL = "https://path.ssu.ac.kr"

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
        SSUPath 공고 목록 페이지를 파싱하여 공고 딕셔너리 목록을 반환합니다.

        Returns:
            list[dict]: 공고 정보 딕셔너리 목록. 각 항목은 아래 필드를 포함합니다:
                - notice_id (str): 공고 고유 ID (encSddpbSeq)
                - status (str): 모집 상태 ("모집중" | "모집대기" | "종료")
                - organizer (str): 운영조직
                - program_format (str): 프로그램 형식
                - title (str): 프로그램명
                - summary (str): 간단 설명
                - application_period (dict): 신청기간 {"start": str, "end": str}
                - education_period (dict): 교육기간 {"start": str, "end": str}
                - target (str): 신청대상
                - target_status (str): 신청신분
                - mileage (int): 지급 마일리지
                - applicant_count (int): 신청자 수
                - waitlist_count (int): 대기자 수
                - capacity (int): 모집 정원
                - competency_tags (list[str]): 역량 태그
                - poster_url (str): 썸네일 이미지 URL
                - source_url (str): 크롤링 원본 URL
        """
        # TODO: 네트워크 오류 시 재시도 로직 추가 필요 (requests.exceptions.RequestException)
        # TODO: 세션 만료(로그인 풀림) 감지 및 자동 재로그인 처리 필요
        #       (응답이 로그인 페이지로 리다이렉트되는 경우 구분 필요)
        res = self.session.get(self.SSUPATH_URL)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select("div[class='lica_wrap'] > ul > li")

        # TODO: items가 비어있을 때 사이트 구조 변경인지 정상 빈 목록인지 구분 필요
        return [
            self._parse_notice(item)
            for item in items
            if item.find('a', class_='detailBtn')
        ]

    def _parse_notice(self, li):
        """공고 li 태그에서 정보를 추출하여 딕셔너리로 반환합니다."""

        # notice_id
        # TODO: data-params JSON 파싱 실패 시 해당 공고를 건너뛰는 예외처리 필요
        detail_a = li.select_one('a.detailBtn[data-params]')
        params = json.loads(detail_a['data-params'])
        notice_id = params.get('encSddpbSeq', '')

        # 상태
        status_tag = li.select_one('div.label_box a span')
        status = status_tag.get_text(strip=True) if status_tag else ''

        # 운영조직, 프로그램 형식
        major_type_items = li.select('ul.major_type li')
        organizer = major_type_items[0].get_text(strip=True) if len(major_type_items) > 0 else ''
        program_format = major_type_items[1].get_text(strip=True) if len(major_type_items) > 1 else ''

        # 제목, 간단설명
        title_tag = li.select_one('a.tit')
        title = title_tag.get_text(strip=True) if title_tag else ''

        desc_tag = li.select_one('p.desc')
        summary = desc_tag.get_text(strip=True) if desc_tag else ''

        # info_wrap의 dl → {dt텍스트: dd텍스트} 매핑
        info_map = {}
        for dl in li.select('div.info_wrap dl'):
            dt = dl.find('dt')
            dd = dl.find('dd')
            if dt and dd:
                info_map[dt.get_text(strip=True)] = dd.get_text(strip=True)

        application_period = self._parse_period(info_map.get('신청기간', ''))
        education_period = self._parse_period(info_map.get('교육기간', ''))
        target = info_map.get('신청대상', '')
        target_status = info_map.get('신청신분', '')

        # etc_cont: 마일리지
        # TODO: 숫자가 아닌 값("-" 등)이 올 경우 int() 변환 오류 방지 처리 필요
        mileage_tag = li.select_one('li.info dl dd')
        mileage = int(mileage_tag.get_text(strip=True)) if mileage_tag else 0

        # etc_cont: 신청자/대기자/모집정원
        # TODO: 동일하게 숫자 이외의 값에 대한 방어 처리 필요
        cnt_map = {}
        for dl in li.select('li.cnt dl'):
            dt = dl.find('dt')
            dd = dl.find('dd')
            if dt and dd:
                cnt_map[dt.get_text(strip=True)] = dd.get_text(strip=True)

        applicant_count = int(cnt_map.get('신청자', 0))
        waitlist_count = int(cnt_map.get('대기자', 0))
        capacity = int(cnt_map.get('모집정원', 0))

        # 역량 태그 (없는 공고도 있음)
        competency_tags = [
            span.get_text(strip=True)
            for span in li.select('li.cabil dl dd span.on')
        ]

        # 포스터 이미지 URL (상대경로 → 절대경로 변환)
        poster_url = ''
        img_tag = li.select_one('div.img_wrap img')
        if img_tag and img_tag.get('src'):
            src = img_tag['src']
            poster_url = f"{self.BASE_URL}{src}" if src.startswith('/') else src

        return {
            'notice_id': notice_id,
            'status': status,
            'organizer': organizer,
            'program_format': program_format,
            'title': title,
            'summary': summary,
            'application_period': application_period,
            'education_period': education_period,
            'target': target,
            'target_status': target_status,
            'mileage': mileage,
            'applicant_count': applicant_count,
            'waitlist_count': waitlist_count,
            'capacity': capacity,
            'competency_tags': competency_tags,
            'poster_url': poster_url,
            'source_url': self.SSUPATH_URL,
        }

    def _parse_period(self, period_str):
        """'2026.03.27 00:00~2026.04.03 00:00' 형태의 기간 문자열을 딕셔너리로 변환합니다."""
        if '~' in period_str:
            start, end = period_str.split('~', 1)
            return {'start': start.strip(), 'end': end.strip()}
        return {'start': period_str.strip(), 'end': ''}

    def get_notice_url(self, notice):
        """
        공고 딕셔너리에서 상세 페이지 URL을 생성합니다.

        Args:
            notice (dict): get_current_page_notices()가 반환한 공고 딕셔너리

        Returns:
            str: 상세 페이지 URL

        Raises:
            KeyError: notice_id 키가 없을 시
        """
        return build_url(self.DETAIL_URL, {'encSddpbSeq': notice['notice_id']})

    def get_detail(self, url):
        pass
