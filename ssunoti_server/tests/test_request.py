from bs4 import BeautifulSoup
from ssunoti.crawler import SsupathCrawler

crawler = SsupathCrawler()
success = crawler.login()

if success:
    print("SUCCESS")
    notices = crawler.get_current_page_notices()
    url = crawler.get_notice_url(notices[0])
    print(url)
else:
    print("FAILED")
