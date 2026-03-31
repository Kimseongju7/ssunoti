from ssunoti.crawler import SsupathCrawler


def test_login_success():
    # login()이 True를 반환하는지 (SSO 로그인 3단계 정상 완료)
    crawler = SsupathCrawler()
    assert crawler.login() is True


def test_login_sets_jsessionid():
    # 로그인 후 path.ssu.ac.kr의 JSESSIONID 쿠키가 발급되는지
    crawler = SsupathCrawler()
    crawler.login()
    cookies = crawler.session.cookies.get_dict()
    assert "JSESSIONID" in cookies
