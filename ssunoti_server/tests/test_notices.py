import pytest
from ssunoti.crawler import SsupathCrawler


@pytest.fixture(scope="module")
def crawler():
    """로그인된 SsupathCrawler 인스턴스.

    모듈 전체에서 단 한 번만 로그인하여 재사용합니다.

    Returns:
        SsupathCrawler: SSO 로그인이 완료된 크롤러 인스턴스
    """
    c = SsupathCrawler()
    c.login()
    return c


@pytest.fixture(scope="module")
def notices(crawler):
    """공고 목록 페이지를 파싱한 결과.

    모듈 전체에서 단 한 번만 요청하여 재사용합니다.

    Returns:
        list[dict]: get_current_page_notices()가 반환한 공고 딕셔너리 목록
    """
    return crawler.get_current_page_notices()


@pytest.fixture(scope="module")
def first_notice(notices):
    """공고 목록의 첫 번째 항목.

    Returns:
        dict: notices[0] 공고 딕셔너리
    """
    return notices[0]


@pytest.fixture(scope="module")
def detail(crawler, first_notice):
    """첫 번째 공고의 상세 정보.

    모듈 전체에서 단 한 번만 요청하여 재사용합니다.

    Returns:
        dict: get_detail()이 반환한 공고 상세 딕셔너리
    """
    url = crawler.get_notice_url(first_notice)
    return crawler.get_detail(url)


# ─────────────────────────────────────────────────
# get_current_page_notices 테스트
# ─────────────────────────────────────────────────

class TestGetCurrentPageNotices:
    """get_current_page_notices()의 반환값 구조를 검증하는 테스트 클래스."""

    def test_returns_nonempty_list(self, notices):
        """공고 목록이 비어있지 않은 리스트인지 검증하고 제목 목록을 출력합니다."""
        assert isinstance(notices, list)
        assert len(notices) > 0
        print(f"\n[공고 목록 — {len(notices)}건]")
        for i, notice in enumerate(notices, 1):
            print(f"  {i:2}. [{notice['status']}] {notice['title']}")

    def test_each_item_is_dict(self, notices):
        """목록의 모든 항목이 딕셔너리인지 검증합니다."""
        for notice in notices:
            assert isinstance(notice, dict)

    def test_required_keys_exist(self, first_notice):
        """공고 딕셔너리에 필수 키 17개가 모두 존재하는지 검증합니다."""
        required_keys = [
            'notice_id', 'status', 'organizer', 'program_format',
            'title', 'summary', 'application_period', 'education_period',
            'target', 'target_status', 'mileage', 'applicant_count',
            'waitlist_count', 'capacity', 'competency_tags',
            'poster_url', 'source_url',
        ]
        for key in required_keys:
            assert key in first_notice, f"키 누락: {key}"

    def test_notice_id_is_nonempty_string(self, notices):
        """notice_id가 비어있지 않은 문자열인지 검증합니다."""
        for notice in notices:
            assert isinstance(notice['notice_id'], str)
            assert len(notice['notice_id']) > 0

    def test_status_is_valid_value(self, notices):
        """status가 허용된 값(모집중/모집대기/종료) 중 하나인지 검증합니다."""
        valid_statuses = {'모집중', '모집대기', '종료'}
        for notice in notices:
            assert notice['status'] in valid_statuses, \
                f"알 수 없는 status 값: {notice['status']}"

    def test_period_has_start_and_end(self, notices):
        """application_period, education_period에 start/end 키가 있는지 검증합니다."""
        for notice in notices:
            for period_key in ('application_period', 'education_period'):
                period = notice[period_key]
                assert 'start' in period and 'end' in period, \
                    f"{period_key} 구조 오류: {period}"

    def test_numeric_fields_are_int(self, notices):
        """mileage, applicant_count, waitlist_count, capacity가 int인지 검증합니다."""
        for notice in notices:
            for key in ('mileage', 'applicant_count', 'waitlist_count', 'capacity'):
                assert isinstance(notice[key], int), \
                    f"{key} 타입 오류: {type(notice[key])}"

    def test_competency_tags_is_list(self, notices):
        """competency_tags가 리스트인지 검증합니다. 태그가 없는 공고는 빈 리스트여야 합니다."""
        for notice in notices:
            assert isinstance(notice['competency_tags'], list)

    def test_poster_url_is_absolute(self, notices):
        """poster_url이 절대 URL(https://)로 변환되어 있는지 검증합니다."""
        for notice in notices:
            if notice['poster_url']:
                assert notice['poster_url'].startswith('https://'), \
                    f"상대 URL 미변환: {notice['poster_url']}"

    def test_notice_url_contains_notice_id(self, crawler, first_notice):
        """get_notice_url()이 반환하는 URL에 encSddpbSeq와 notice_id가 포함되어 있는지 검증합니다."""
        url = crawler.get_notice_url(first_notice)
        assert url.startswith("https://path.ssu.ac.kr")
        assert "encSddpbSeq" in url
        assert first_notice['notice_id'] in url


# ─────────────────────────────────────────────────
# get_detail 테스트
# ─────────────────────────────────────────────────

class TestGetDetail:
    """get_detail()의 반환값 구조를 검증하는 테스트 클래스."""

    def test_returns_dict(self, detail):
        """반환값이 딕셔너리인지 검증하고 main_content를 출력합니다."""
        assert isinstance(detail, dict)
        print(f"\n[공고 상세 — {detail['title']}]")
        print(f"{detail['main_content']}")

    def test_required_keys_exist(self, detail):
        """상세 딕셔너리에 필수 키 27개가 모두 존재하는지 검증합니다."""
        required_keys = [
            'title', 'organizer', 'manager_email', 'manager_phone',
            'program_type', 'semester', 'category', 'program_format',
            'goal', 'summary', 'operation_method', 'application_method',
            'application_period', 'selection_method', 'target', 'target_status',
            'target_detail', 'capacity', 'waitlist_capacity', 'attachments',
            'has_certificate', 'mileage', 'core_competencies',
            'main_content', 'course_info', 'sessions', 'source_url',
        ]
        for key in required_keys:
            assert key in detail, f"키 누락: {key}"

    def test_semester_structure(self, detail):
        """semester가 year(int), term(int) 키를 가진 딕셔너리인지 검증합니다."""
        semester = detail['semester']
        assert 'year' in semester and 'term' in semester
        assert isinstance(semester['year'], int)
        assert isinstance(semester['term'], int)

    def test_application_period_structure(self, detail):
        """application_period에 start/end 키가 있는지 검증합니다."""
        period = detail['application_period']
        assert 'start' in period and 'end' in period

    def test_capacity_fields_are_int(self, detail):
        """capacity, waitlist_capacity가 int인지 검증합니다."""
        assert isinstance(detail['capacity'], int)
        assert isinstance(detail['waitlist_capacity'], int)

    def test_has_certificate_is_bool(self, detail):
        """has_certificate가 bool인지 검증합니다."""
        assert isinstance(detail['has_certificate'], bool)

    def test_mileage_is_int(self, detail):
        """mileage가 int인지 검증합니다."""
        assert isinstance(detail['mileage'], int)

    def test_attachments_is_list(self, detail):
        """attachments가 리스트이고 각 항목에 name/url 키가 있는지 검증합니다."""
        assert isinstance(detail['attachments'], list)
        for attachment in detail['attachments']:
            assert 'name' in attachment and 'url' in attachment

    def test_core_competencies_structure(self, detail):
        """core_competencies 각 항목에 keyword(str), ratio(0~100 int)가 있는지 검증합니다."""
        assert isinstance(detail['core_competencies'], list)
        for comp in detail['core_competencies']:
            assert 'keyword' in comp and 'ratio' in comp
            assert isinstance(comp['ratio'], int)
            assert 0 <= comp['ratio'] <= 100

    def test_course_info_structure(self, detail):
        """course_info에 semester, has_attendance(bool), progress_type 키가 있는지 검증합니다."""
        course_info = detail['course_info']
        assert 'semester' in course_info
        assert 'has_attendance' in course_info
        assert 'progress_type' in course_info
        assert isinstance(course_info['has_attendance'], bool)

    def test_sessions_is_list(self, detail):
        """sessions가 리스트인지 검증합니다."""
        assert isinstance(detail['sessions'], list)

    def test_session_structure(self, detail):
        """sessions 각 항목의 필수 키와 타입을 검증합니다.

        session_no(int), has_assignment(bool)은 타입까지, 나머지 6개 키는 존재 여부만 확인합니다.
        """
        for session in detail['sessions']:
            assert 'session_no' in session
            assert 'class_name' in session
            assert 'education_period' in session
            assert 'location' in session
            assert 'instructor' in session
            assert 'attachments' in session
            assert 'has_assignment' in session
            assert 'assignment_period' in session
            assert isinstance(session['session_no'], int)
            assert isinstance(session['has_assignment'], bool)

    def test_source_url_is_detail_url(self, detail):
        """source_url이 상세 페이지 URL(findIcmpNsbjtPgmInfo.do + encSddpbSeq)인지 검증합니다."""
        assert 'findIcmpNsbjtPgmInfo.do' in detail['source_url']
        assert 'encSddpbSeq' in detail['source_url']
