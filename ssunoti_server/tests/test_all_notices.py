import pytest
from ssunoti.crawler import SsupathCrawler, NoDataError
from ssunoti.utils import build_url


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
def all_notices_2026(crawler):
    """2026년 전체 공고 목록.

    모듈 전체에서 단 한 번만 수집하여 재사용합니다.

    Returns:
        list[dict]: get_all_notices(year=2026)가 반환한 전체 공고 목록
    """
    notices = crawler.get_all_notices(year=2026)
    print(f"\n[2026년 전체 공고 — {len(notices)}건]")
    for i, n in enumerate(notices, 1):
        print(f"  {i:3}. [{n['status']}] {n['title']}")
    return notices


@pytest.fixture(scope="module")
def recruiting_notices(crawler):
    """2026년 모집중(RS02) 공고 목록.

    Returns:
        list[dict]: get_all_notices(year=2026, status='RS02')가 반환한 공고 목록
    """
    return crawler.get_all_notices(year=2026, status='RS02')


# ─────────────────────────────────────────────────
# get_all_notices 테스트
# ─────────────────────────────────────────────────

class TestGetAllNotices:
    """get_all_notices()의 페이지 순회 및 필터링 동작을 검증하는 테스트 클래스."""

    def test_returns_nonempty_list(self, all_notices_2026):
        """전체 공고 목록이 비어있지 않은 리스트인지 검증합니다."""
        assert isinstance(all_notices_2026, list)
        assert len(all_notices_2026) > 0

    def test_more_than_one_page(self, all_notices_2026):
        """페이지 순회가 실제로 이루어져 한 페이지(10건) 이상을 수집하는지 검증합니다."""
        assert len(all_notices_2026) > 10

    def test_each_item_is_dict(self, all_notices_2026):
        """모든 항목이 딕셔너리인지 검증합니다."""
        for notice in all_notices_2026:
            assert isinstance(notice, dict)

    def test_no_duplicate_notice_ids(self, all_notices_2026):
        """페이지를 넘어가며 동일한 공고가 중복 수집되지 않는지 검증합니다."""
        ids = [n['notice_id'] for n in all_notices_2026]
        assert len(ids) == len(set(ids)), "중복된 notice_id가 존재합니다"

    def test_status_filter_recruiting_only(self, recruiting_notices):
        """status='RS02' 필터 적용 시 모든 공고가 '모집중' 상태인지 검증합니다."""
        assert len(recruiting_notices) > 0
        for notice in recruiting_notices:
            assert notice['status'] == '모집중', \
                f"예상하지 못한 status: {notice['status']}"

    def test_status_filter_reduces_count(self, all_notices_2026, recruiting_notices):
        """status 필터를 적용하면 전체보다 적은 수의 공고가 반환되는지 검증합니다."""
        assert len(recruiting_notices) <= len(all_notices_2026)

    def test_source_url_contains_page_param(self, all_notices_2026):
        """두 번째 페이지 이후 공고의 source_url에 페이지 번호 파라미터가 있는지 검증합니다."""
        if len(all_notices_2026) > 10:
            second_page_notice = all_notices_2026[10]
            assert 'currentPageNo' in second_page_notice['source_url']


# ─────────────────────────────────────────────────
# NoDataError 테스트
# ─────────────────────────────────────────────────

class TestNoDataError:
    """get_current_page_notices()의 NoDataError 발생 동작을 검증하는 테스트 클래스."""

    def test_raises_on_empty_page(self, crawler):
        """데이터가 없는 페이지 요청 시 NoDataError가 발생하는지 검증합니다."""
        empty_url = build_url(
            crawler.SSUPATH_URL,
            {
                'paginationInfo.currentPageNo': 9999,
                'sort': '0001',
                'chkAblyCount': '0',
                'operYySh': '2026',
                'operSemCdSh': '0000',
                'operSemCdShVal': '0000',
                'vshOrgid': '',
                'vshOrgzNm': '',
                'recStaCdSh': '0000',
                'searchValue': '',
                'prgmFormCdSh': '0000',
                'prgmFormCdShVal': '0000',
                'eduFrDt': '',
                'eduToDt': '',
                'scpfDpmtCdSh': '',
                'scpfDpmtCdNm': '',
            }
        )
        with pytest.raises(NoDataError):
            crawler.get_current_page_notices(empty_url)

    def test_error_message_contains_url(self, crawler):
        """NoDataError 메시지에 요청 URL이 포함되어 있는지 검증합니다."""
        empty_url = build_url(
            crawler.SSUPATH_URL,
            {'paginationInfo.currentPageNo': 9999, 'sort': '0001',
             'chkAblyCount': '0', 'operYySh': '2026', 'operSemCdSh': '0000',
             'operSemCdShVal': '0000', 'vshOrgid': '', 'vshOrgzNm': '',
             'recStaCdSh': '0000', 'searchValue': '', 'prgmFormCdSh': '0000',
             'prgmFormCdShVal': '0000', 'eduFrDt': '', 'eduToDt': '',
             'scpfDpmtCdSh': '', 'scpfDpmtCdNm': ''},
        )
        with pytest.raises(NoDataError, match='조회된 데이터가 없습니다'):
            crawler.get_current_page_notices(empty_url)
