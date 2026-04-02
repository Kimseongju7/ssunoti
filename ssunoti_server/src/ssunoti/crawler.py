import json
import os
import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

from ssunoti.utils import build_url

load_dotenv()


class NoDataError(Exception):
    """공고 목록 페이지에 조회된 데이터가 없을 때 발생하는 예외."""
    pass


class SsupathCrawler:

    SSO_LOGIN_PAGE = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp"
    SSO_LOGIN_PROCESS = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
    API_RETURN_URL = "https://path.ssu.ac.kr/comm/login/user/loginProc.do?rtnUrl=/index.do?paramStart=paramStart"
    SSUPATH_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do"
    DETAIL_URL = "https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmInfo.do"
    BASE_URL = "https://path.ssu.ac.kr"

    _SESSION_CHECK_INTERVAL = timedelta(minutes=10)

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.getenv("user_agent"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9",
        })
        self._last_verified_at = None

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

    def is_session_valid(self):
        """세션이 유효한지 확인합니다.

        SSUPATH_URL 에 GET 요청을 보내고 로그인 후에만 존재하는
        div.lica_wrap 의 유무로 판단합니다.
        세션이 만료되면 로그인 페이지가 반환되어 lica_wrap 이 없습니다.

        Returns:
            bool: 세션이 유효하면 True, 만료되었으면 False
        """
        res = self.session.get(self.SSUPATH_URL)
        soup = BeautifulSoup(res.text, 'lxml')
        return bool(soup.select_one('div.lica_wrap'))

    def _ensure_session(self):
        """세션이 유효하지 않으면 재로그인합니다.

        마지막 확인 시각으로부터 10분 이내면 is_session_valid() 호출을 건너뜁니다.
        10분이 지났거나 첫 호출이면 세션을 확인하고, 만료 시 재로그인합니다.

        get_current_page_notices(), get_detail() 등 인증이 필요한 요청 전에 호출됩니다.
        """
        now = datetime.now()
        if self._last_verified_at and (now - self._last_verified_at) < self._SESSION_CHECK_INTERVAL:
            return

        if not self.is_session_valid():
            self.login()

        self._last_verified_at = now

    def get_current_page_notices(self, url=None):
        """
        공고 목록 페이지를 파싱하여 공고 딕셔너리 목록을 반환합니다.

        Args:
            url (str | None): 요청할 공고 목록 페이지 URL.
                None이면 기본 목록 URL(SSUPATH_URL)을 사용합니다.
                get_all_notices()가 페이지별 URL을 넘길 때 이 파라미터를 사용합니다.

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

        Raises:
            NoDataError: 해당 페이지에 조회된 공고가 없을 때 (li.NO_RESULT 감지)
        """
        # TODO: 네트워크 오류 시 재시도 로직 추가 필요 (requests.exceptions.RequestException)
        self._ensure_session()

        if url is None:
            url = self.SSUPATH_URL

        res = self.session.get(url)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'lxml')

        if soup.select_one('li.NO_RESULT'):
            raise NoDataError(f"조회된 데이터가 없습니다: {url}")

        items = soup.select("div[class='lica_wrap'] > ul > li")
        return [
            self._parse_notice(item, source_url=url)
            for item in items
            if item.find('a', class_='detailBtn')
        ]

    def _parse_notice(self, li, source_url=None):
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
            'source_url': source_url or self.SSUPATH_URL,
        }

    def _parse_period(self, period_str):
        """'2026.03.27 00:00~2026.04.03 00:00' 형태의 기간 문자열을 딕셔너리로 변환합니다.

        &nbsp;(\xa0)로 구분된 '2026.03.27 00:00\xa0~\xa02026.04.03 00:00' 형태도 처리합니다.
        """
        clean = period_str.replace('\xa0', ' ').strip()
        if '~' in clean:
            start, end = clean.split('~', 1)
            return {'start': start.strip(), 'end': end.strip()}
        return {'start': clean, 'end': ''}

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

    def get_all_notices(self, year=None, status='0000', semester='0000'):
        """
        페이지를 순회하면서 조건에 맞는 모든 공고를 수집합니다.

        각 페이지를 get_current_page_notices()로 요청하고,
        NoDataError가 발생하면 순회를 종료합니다.

        Args:
            year (int | None): 운영년도. None이면 현재 연도를 사용합니다.
            status (str): 모집 상태 코드. 기본값 '0000' (전체).
                - '0000': 전체
                - 'RS01': 모집대기
                - 'RS02': 모집중
                - 'RS03': 종료
            semester (str): 학기 코드. 기본값 '0000' (전체).
                - '0000': 전체
                - '0001': 1학기
                - '0003': 2학기

        Returns:
            list[dict]: 전체 공고 딕셔너리 목록.
                각 항목의 구조는 get_current_page_notices() 참고.

        Example:
            >>> notices = crawler.get_all_notices(year=2026, status='RS02')
            >>> print(len(notices))  # 모집중 공고 전체 수
        """
        if year is None:
            year = datetime.now().year

        all_notices = []
        page = 1

        while True:
            url = build_url(self.SSUPATH_URL, {
                'paginationInfo.currentPageNo': page,
                'sort': '0001',
                'chkAblyCount': '0',
                'operYySh': str(year),
                'operSemCdSh': semester,
                'operSemCdShVal': semester,
                'vshOrgid': '',
                'vshOrgzNm': '',
                'recStaCdSh': status,
                'searchValue': '',
                'prgmFormCdSh': '0000',
                'prgmFormCdShVal': '0000',
                'eduFrDt': '',
                'eduToDt': '',
                'scpfDpmtCdSh': '',
                'scpfDpmtCdNm': '',
            })

            try:
                page_notices = self.get_current_page_notices(url)
            except NoDataError:
                break

            all_notices.extend(page_notices)
            page += 1

        return all_notices

    def get_detail(self, url):
        """
        공고 상세 페이지를 파싱하여 상세 정보 딕셔너리를 반환합니다.

        Args:
            url (str): 공고 상세 페이지 URL (get_notice_url()로 생성)

        Returns:
            dict: 공고 상세 정보. 아래 필드를 포함합니다:
                - title (str): 프로그램명
                - organizer (str): 운영조직
                - manager_email (str): 담당자 이메일
                - manager_phone (str): 담당자 번호
                - program_type (str): 프로그램 유형
                - semester (dict): 운영년도/학기 {"year": int, "term": int}
                - category (str): 프로그램 분류
                - program_format (str): 프로그램 형식
                - goal (str): 프로그램 목표
                - summary (str): 프로그램 한줄 소개
                - operation_method (str): 운영방식
                - application_method (str): 신청방법
                - application_period (dict): 신청기간 {"start": str, "end": str}
                - selection_method (str): 선정방법
                - target (str): 신청대상
                - target_status (str): 신청신분
                - target_detail (dict): 학생 신청대상 상세정보
                    {"academic_status": str, "division": str, "grade_years": str}
                - capacity (int): 정원
                - waitlist_capacity (int): 대기자 정원
                - attachments (list[dict]): 첨부파일 [{"name": str, "url": str}]
                - has_certificate (bool): 이수 인증서 여부
                - mileage (int): 지급 마일리지
                - core_competencies (list[dict]): 핵심역량 비중도
                    [{"keyword": str, "ratio": int}]
                - main_content (str): 프로그램 주요내용 (plain text)
                - course_info (dict): 강좌 기본정보
                    {"semester": str, "has_attendance": bool, "progress_type": str}
                - sessions (list[dict]): 회차별 정보
                - source_url (str): 크롤링 원본 URL
        """
        # TODO: 네트워크 오류 시 재시도 로직 추가 필요
        self._ensure_session()

        res = self.session.get(url)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'lxml')
        con_box = soup.find('div', id='tilesContent')

        # 프로그램 제목
        title_tag = con_box.select_one('div.table_top h4')
        title = title_tag.get_text(strip=True) if title_tag else ''

        # 메인 테이블 th → td 매핑
        main_tbody = con_box.select_one('table.t_view tbody')
        field_map = self._build_field_map(main_tbody)

        # 단순 텍스트 필드 (키는 공백 제거 정규화 버전 사용 — _build_field_map 참고)
        organizer          = self._td_text(field_map, '운영조직')
        manager_email      = self._td_text(field_map, '담당자이메일')
        manager_phone      = self._td_text(field_map, '담당자번호')
        program_type       = self._td_text(field_map, '프로그램유형')
        category           = self._td_text(field_map, '프로그램분류')
        program_format     = self._td_text(field_map, '프로그램형식')
        goal               = self._td_text(field_map, '프로그램목표')
        summary            = self._td_text(field_map, '프로그램한줄소개')
        operation_method   = self._td_text(field_map, '운영방식')
        application_method = self._td_text(field_map, '신청방법')
        selection_method   = self._td_text(field_map, '선정방법')
        target_status      = self._td_text(field_map, '신청신분')

        # 운영년도/학기 → {"year": int, "term": int}
        semester = self._parse_semester(self._td_text(field_map, '운영년도/학기'))

        # 신청기간 (키 정규화로 '신청기간' / '신청 기간' 모두 동일하게 처리됨)
        application_period = self._parse_period(self._td_text(field_map, '신청기간'))

        # 신청대상 (ul.ul_chk > li 목록)
        target = ''
        if '신청대상' in field_map:
            target_items = field_map['신청대상'].select('ul.ul_chk li')
            target = ', '.join(li.get_text(strip=True) for li in target_items) if target_items \
                else field_map['신청대상'].get_text(strip=True)

        # 학생 신청대상 상세정보 (dt 키도 공백 제거 정규화)
        target_detail = {}
        if '학생신청대상상세정보' in field_map:
            for dl in field_map['학생신청대상상세정보'].find_all('dl', class_='flex_dl'):
                dt = dl.find('dt')
                dd = dl.find('dd')
                if dt and dd:
                    key = ''.join(dt.get_text(strip=True).split()).rstrip(':')
                    target_detail[key] = ' '.join(dd.get_text(strip=True).replace('\xa0', ' ').split())

        # 정원 / 대기자 (혼합 텍스트 → 숫자 추출)
        capacity, waitlist_capacity = 0, 0
        if '정원/대기자' in field_map:
            numbers = re.findall(r'\d+', field_map['정원/대기자'].get_text())
            capacity          = int(numbers[0]) if len(numbers) > 0 else 0
            waitlist_capacity = int(numbers[1]) if len(numbers) > 1 else 0

        # 첨부파일
        attachments = self._parse_attachments(field_map.get('첨부파일'))

        # 이수 인증서
        has_certificate = self._td_text(field_map, '이수인증서') == 'O'

        # 지급 마일리지
        mileage_str = self._td_text(field_map, '지급마일리지')
        mileage = int(mileage_str) if mileage_str.isdigit() else 0

        # 핵심역량 비중도
        core_competencies = []
        if '핵심역량비중도' in field_map:
            for li in field_map['핵심역량비중도'].select('ul.ul_chk li'):
                keyword_tag = li.find('span')
                ratio_tag   = li.find('strong')
                if keyword_tag and ratio_tag:
                    core_competencies.append({
                        'keyword': keyword_tag.get_text(strip=True),
                        'ratio':   int(ratio_tag.get_text(strip=True)),
                    })

        # 프로그램 주요내용 (CKEditor HTML → plain text, 줄바꿈 보존)
        main_content = ''
        if '프로그램주요내용' in field_map:
            content_div = field_map['프로그램주요내용'].select_one('.ck-contentEditDiv')
            main_content = content_div.get_text(separator='\n', strip=True) if content_div else \
                field_map['프로그램주요내용'].get_text(separator='\n', strip=True)

        # 강좌 정보 (id 중복 → find_all로 전체 수집)
        course_blocks = con_box.find_all('div', id='intlNsbjtLtrInfoList')
        course_info = self._parse_course_info(course_blocks[0]) if course_blocks else {}
        sessions    = [self._parse_session(block) for block in course_blocks[1:]]

        return {
            'title':              title,
            'organizer':          organizer,
            'manager_email':      manager_email,
            'manager_phone':      manager_phone,
            'program_type':       program_type,
            'semester':           semester,
            'category':           category,
            'program_format':     program_format,
            'goal':               goal,
            'summary':            summary,
            'operation_method':   operation_method,
            'application_method': application_method,
            'application_period': application_period,
            'selection_method':   selection_method,
            'target':             target,
            'target_status':      target_status,
            'target_detail':      target_detail,
            'capacity':           capacity,
            'waitlist_capacity':  waitlist_capacity,
            'attachments':        attachments,
            'has_certificate':    has_certificate,
            'mileage':            mileage,
            'core_competencies':  core_competencies,
            'main_content':       main_content,
            'course_info':        course_info,
            'sessions':           sessions,
            'source_url':         url,
        }

    def _build_field_map(self, tbody):
        """tbody 안의 모든 th[scope=row] → 바로 다음 td를 매핑한 딕셔너리를 반환합니다.

        키는 내부 공백을 모두 제거하여 정규화합니다.
        예: '신청 기간' → '신청기간', '프로그램 유형' → '프로그램유형'
        HTML 작성 방식의 차이(공백 유무)로 인한 키 미스매치를 방지합니다.
        """
        field_map = {}
        for th in tbody.find_all('th', scope='row'):
            td = th.find_next_sibling('td')
            if td:
                key = ''.join(th.get_text(strip=True).split())
                field_map[key] = td
        return field_map

    def _td_text(self, field_map, key):
        """field_map에서 key에 해당하는 td의 텍스트를 반환합니다. 없으면 빈 문자열.

        &nbsp;(\xa0)를 일반 공백으로 변환하고, 각 줄의 내부 공백을 정규화합니다.
        HTML 들여쓰기로 인한 \n\t 노이즈와 이중 공백을 제거합니다.
        """
        td = field_map.get(key)
        if not td:
            return ''
        text = td.get_text(separator='\n', strip=True).replace('\xa0', ' ')
        lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
        return ' '.join(lines)

    def _parse_semester(self, semester_str):
        """'2026년 1학기' 또는 '2026/1학기' 형태를 {"year": int, "term": int}으로 변환합니다.
        년/슬래시 뒤에 공백이 있어도 처리합니다 (예: '2026년 1학기').
        """
        match = re.search(r'(\d{4})[년/]\s*(\d+)', semester_str)
        if match:
            return {'year': int(match.group(1)), 'term': int(match.group(2))}
        return {'year': 0, 'term': 0}

    def _parse_attachments(self, td):
        """첨부파일 td에서 파일 목록을 추출합니다. td가 없으면 빈 리스트."""
        if not td:
            return []
        return [
            {
                'name': a.get_text(strip=True),
                'url':  f"{self.BASE_URL}{a['href']}" if a.get('href', '').startswith('/') else a.get('href', ''),
            }
            for a in td.select('ul.cmnFileLst li a')
            if a.get('href')
        ]

    def _parse_course_info(self, block):
        """강좌 기본정보 블록(첫 번째 intlNsbjtLtrInfoList)을 파싱합니다."""
        rows = block.select('table tbody tr')
        row_texts = [row.find('td').get_text(strip=True) if row.find('td') else '' for row in rows]
        return {
            'semester':      row_texts[0] if len(row_texts) > 0 else '',
            'has_attendance': row_texts[1] == 'Y' if len(row_texts) > 1 else False,
            'progress_type': row_texts[2] if len(row_texts) > 2 else '',
        }

    def _parse_session(self, block):
        """회차 블록(두 번째 이후 intlNsbjtLtrInfoList)을 파싱합니다."""
        # 회차 번호 (rowspan이 있는 th)
        session_no = 0
        session_th = block.find('th', attrs={'rowspan': True})
        if session_th:
            match = re.search(r'\d+', session_th.get_text())
            session_no = int(match.group()) if match else 0

        # 나머지 필드: rowspan 없는 th → 다음 td
        session_map = {}
        for th in block.find_all('th'):
            if not th.get('rowspan'):
                td = th.find_next_sibling('td')
                if td:
                    session_map[th.get_text(strip=True)] = td

        # 교육기간
        education_period = self._parse_period(
            session_map['교육기간'].get_text(strip=True) if '교육기간' in session_map else ''
        )

        # 교육장소 / 강사 (슬래시로 분리)
        location, instructor = '', ''
        if '교육장소/강사' in session_map:
            parts = session_map['교육장소/강사'].get_text(strip=True).split('/', 1)
            location   = parts[0].strip()
            instructor = parts[1].strip() if len(parts) > 1 else ''

        # 강좌명
        class_name = session_map['강좌명'].get_text(strip=True) if '강좌명' in session_map else ''

        # 첨부파일
        attachments = self._parse_attachments(session_map.get('첨부파일'))

        # 과제 제출 여부 및 기간
        has_assignment = False
        assignment_period = {'start': '', 'end': ''}
        if '과제제출' in session_map:
            td = session_map['과제제출']
            b_tag = td.find('b')
            has_assignment = b_tag.get_text(strip=True) == '제출' if b_tag else False
            period_span = td.find('span', class_='pl20')
            if period_span:
                assignment_period = self._parse_period(period_span.get_text(strip=True))

        return {
            'session_no':        session_no,
            'class_name':        class_name,
            'education_period':  education_period,
            'location':          location,
            'instructor':        instructor,
            'attachments':       attachments,
            'has_assignment':    has_assignment,
            'assignment_period': assignment_period,
        }
