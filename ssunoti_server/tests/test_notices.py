import pytest
from crawling.ssupath_crawling import SsupathCrawler


@pytest.fixture(scope="module")
def crawler():
    """로그인된 크롤러 인스턴스 (모듈 전체에서 재사용)"""
    c = SsupathCrawler()
    c.login()
    return c


def test_get_current_page_notices_returns_list(crawler):
    # 공고 목록이 비어있지 않은 리스트로 반환되는지
    notices = crawler.get_current_page_notices()
    assert isinstance(notices, list)
    assert len(notices) > 0


def test_get_notice_url_format(crawler):
    # 공고 URL이 올바른 도메인과 encSddpbSeq 파라미터를 포함하는지
    notices = crawler.get_current_page_notices()
    url = crawler.get_notice_url(notices[0])
    assert url.startswith("https://path.ssu.ac.kr")
    assert "encSddpbSeq" in url
